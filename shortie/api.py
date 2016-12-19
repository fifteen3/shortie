from flask import Flask, request, abort, redirect
from werkzeug.contrib.fixers import ProxyFix
import hashlib
import db

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def root_route():
    return "Welcome to Shortie."


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


if __name__ == '__main__':
    app.run()
