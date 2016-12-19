import pytest
import re
from shortie import api

@pytest.fixture
def client():
    client = api.app.test_client()
    return client

def test_root(client):
    response = client.get('/')
    assert u'Welcome to Shortie.' in response.data

def test_encode():
    url = "http://www.foo.com"
    user = "user@users.com"
    long_hash = api.encode_url(url,user)
    pattern = '[A-Za-z0-9]+'
    assert re.match(pattern, long_hash)

def test_shorten_url():

    url = "http://www.foo.com"
    user = "user@users.com"
    long_hash = api.encode_url(url,user)
    shortie = api.shorten_url(long_hash)
    assert long_hash[:7] in  shortie

