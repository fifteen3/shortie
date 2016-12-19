from flask import Flask, request, abort, redirect
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def root_route():
    return "Welcome to Shortie."


if __name__ == '__main__':
    app.run()
