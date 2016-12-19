import pytest
import json
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

def test_get_user_id():
    email = 'jason@seaver.com'
    actual_user_id = api.get_user_id(email)
    expected = 1
    assert (expected == actual_user_id)

def test_store_urls(client):
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    payload = json.dumps({ 'user' : 'jason@seaver.com', 'urls' : urls })
    expected =  api.encode_url(urls['desktop'],'jason@seaver.com')[:7]
    response = client.post('/shorten', data=payload, content_type = 'application/json')
    actual = json.loads(response.data)
    assert (expected in actual['data'][0]['shortie'])
