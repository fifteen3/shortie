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
    payload = json.dumps({ 'urls' : urls })
    expected =  api.encode_url(urls['desktop'],'jason@seaver.com')[:7]
    response = client.post('/api/v1/user/jason@seaver.com/urls', data=payload, content_type = 'application/json')
    actual = json.loads(response.data)
    assert (expected in actual['data'][0]['shortie'])

def test_redirect_desktop(client):
    expected = 'https://test.desktop'
    actual = True
    ua_string = '''Mozilla/5.0 (MacOs) AppleWebKit/534.46 (KHTML, like Gecko)'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_mobile(client):
    expected = 'https://test.mobile'
    actual = True
    ua_string = '''Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_tablet(client):
    ua_string = '''Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'''
    expected = 'https://test.tablet'
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)
