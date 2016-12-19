from flask import Flask, request, abort, redirect
from werkzeug.contrib.fixers import ProxyFix
import json
import re
import db
from user import User
from url_assistant import UrlFinder,UrlEncoder,UrlSaver

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
fqdn = "http://localhost:9001"

@app.route("/")
def root_route():
    return "Welcome to Shortie."

# redirect to device specific url
@app.route("/<url_hash>")
def short_route(url_hash):

    data = []
    errors = []

    if (re.match("[A-Za-z0-9]{7,10}",url_hash)):
        ua_string = request.headers.get('User-Agent');

        url_finder = UrlFinder(db=db,url_hash=url_hash,ua_string=ua_string)
        url = url_finder.lookup_url()

        if url:
            return redirect(url,code=302)

    abort(404)

# save a set of urls for a user
@app.route("/api/v1/users/<email>/urls", methods=["POST"])
def shorten(email):
    if  not request.get_json():
        abort(400)
    data = []
    errors = []
    user = User(db=db,email=email)

    # desktop will be the url used to hash
    urls =  request.get_json()['urls']
    url =  urls['desktop']
    url_encoder = UrlEncoder(url=url)
    encoded_url = url_encoder.encode_url(user)

    url_saver = UrlSaver(db)
    url_saver.store_urls(urls,encoded_url,user)

    shortened_url = "{}/{}".format(fqdn,encoded_url[:7])

    if (shortened_url):
        data.append({ "shortie" : shortened_url })
    else:
        errors.append({"message" : "save failed."})
    return format_json_response(data,errors,len(data))

# get list of user's urls
@app.route("/api/v1/users/<email>/urls")
def url_list(email):
   user = User(db=db,email=email)
   urls = user.list_urls()
   errors = []
   return format_json_response(urls,errors,len(urls))

def format_json_response(data,errors,total):
    """api response format"""
    meta = {}
    meta["errors"] = errors
    meta["total"] = total

    response = {}
    response['data'] = data
    response['meta'] = meta

    return json.dumps(response)

if __name__ == '__main__':
    app.run()
