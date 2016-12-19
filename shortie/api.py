from flask import Flask, request, abort, redirect
from werkzeug.contrib.fixers import ProxyFix
import user_agents
import json
import hashlib
import re
import sqlite3
import db

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def root_route():
    return "Welcome to Shortie."

@app.route("/<url_hash>")
def short_route(url_hash):

    data = []
    errors = []
    if (re.match("[A-Za-z0-9]{7,10}",url_hash)):
        ua_string = request.headers.get('User-Agent');
        device = lookup_device_type(ua_string)
        url = lookup_url(url_hash,device)
        if url:
            return redirect(url,code=302)

    abort(404)

@app.route("/api/v1/user/<user_id>/urls", methods=["POST"])
def shorten(user_id):
    if  not request.get_json():
        abort(400)
    data = []
    errors = []
    urls =  request.get_json()['urls']
    user = user_id #request.get_json()['user']
    # desktop will be the url used to hash
    url =  request.get_json()['urls']['desktop']
    encoded_url = encode_url(url,user)
    store_urls(urls,encoded_url,user)
    shortened_url = "https://localhost:5000/%s" % encoded_url[:7]

    if (True):
        data.append({ "shortie" : shortened_url })
    else:
        errors.append({"message" : "save failed."})
    return format_json_response(data,errors)

def store_urls(urls,encoded_url,user):
    conn = db.get_db()
    c = conn.cursor()
    if not c:
        return "Database connection Error."
    #generate the uuid and insert it and
    shortie = encoded_url[:7]
    try:
        insert_hash_query = 'INSERT INTO url_hashes (short_hash,long_hash,user_id) VALUES (?,?,?)'
        user_id = get_user_id(user)
        c.execute(insert_hash_query, [shortie,encoded_url,user_id])
        for url_type,url in urls.iteritems():
            try:
                insert_url_query = 'INSERT INTO urls (short_hash,url_type,url) VALUES (?,?,?)'
                c.execute(insert_url_query, [shortie, url_type, url])
            except sqlite3.Error as e:
                print e.message
    except sqlite3.Error as e:
       print e.message
    conn.commit()

def get_user_id(email):
    c = db.get_db().cursor()
    if not c:
        return None
    try:
        print email
        c.execute('SELECT rowid FROM users WHERE email = ?', [email])
        user_id = c.fetchone()[0]
        return user_id
    except (TypeError,sqlite3.Error) as e:
        print e.message

def format_json_response(data,errors):
    meta = {}
    meta["errors"] = errors
    meta["total"] = len(data)
    response = {}
    response['data'] = data
    response['meta'] = meta
    return json.dumps(response)

def shorten_url(long_hash):
    host = 'http://localhost:5000'
    shortened_url = "{}{}".format(host,  long_hash[:7])
    return shortened_url

def encode_url(url,user):
    url_bytes = url.encode('utf-8')
    user_bytes = user.encode('utf-8')
    m = hashlib.sha1(url_bytes + user_bytes)
    long_hash = m.hexdigest()
    return long_hash

def lookup_url(url_hash,device):
    conn = db.get_db()
    c = conn.cursor()
    c.execute('SELECT url FROM urls WHERE short_hash = ? AND url_type = ?', [url_hash, device])
    url = c.fetchone()[0]
    if url:
        try:
            c.execute('INSERT INTO visits (short_hash,url_type) VALUES (?,?)', [url_hash,device])
            conn.commit()
        except sqlite3.Error as e:
            print e.message
        return url

def lookup_device_type(ua_string):
    dt = "desktop"
    ua = user_agents.parse(ua_string)
    if ua.is_mobile:
        dt = "mobile"
    elif ua.is_tablet:
        dt = "tablet"
    return dt

if __name__ == '__main__':
    app.run()
