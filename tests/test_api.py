import pytest
import json
import re
from shortie import api,manage

@pytest.fixture(scope='function')
def client(request):
    #setup
    client = api.app.test_client()
    print "create db."
    manage.create_db()
    print "populate db."
    manage.pop_db()
    yield client
    #teardown
    print "delete db."
    manage.delete_db()

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

def test_get_user_id(client):
    email = 'jason@seaver.com'
    actual_user_id = api.get_user_id(email)
    expected = 1
    assert (expected == actual_user_id)

def test_store_urls(client):
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    actual = insert_case(client,urls)
    expected =  api.encode_url(urls['desktop'],'jason@seaver.com')[:7]
    assert (expected in actual['data'][0]['shortie'])

def test_redirect_desktop(client):
    expected = 'https://test.desktop'
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0 (MacOs) AppleWebKit/534.46 (KHTML, like Gecko)'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_mobile(client):
    expected = 'https://test.mobile'
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_tablet(client):
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'''
    expected = 'https://test.tablet'
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_user_urls(client):
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    response = insert_case(client,urls)
    short_url = response['data'][0]['shortie']
    request_redirect(client,short_url)
    request_redirect(client,short_url)
    request_redirect(client,short_url)
    rows = api.list_urls_by_user('jason@seaver.com')
    assert (len(rows) > 0)
    for row in rows:
        assert (row['url'])
        assert (row['url_type'] and re.match("mobile|tablet|desktop",row['url_type']))
        assert (row['visits'] and row['visits'] == 3)
        assert (row['since'])

def insert_case(tclient,urls):
    payload = json.dumps({ 'urls' : urls })
    response = tclient.post('/api/v1/users/jason@seaver.com/urls', data=payload, content_type = 'application/json')
    actual = json.loads(response.data)
    return actual

def request_redirect(tclient,short_url):
    ua_string = '''Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'''
    headers = { 'User-Agent' : ua_string }
    actual = tclient.get(short_url,headers=headers).data
