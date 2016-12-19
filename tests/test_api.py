import pytest
import json
import re
from shortie import api,manage,db
from shortie.url_assistant import UrlEncoder
from shortie.user import User

@pytest.fixture(scope='function')
def client(request):
    """Provide the test client and set up the database for running tests"""
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
    """Simple test to prove the root url works"""
    response = client.get('/')
    assert u'Welcome to Shortie.' in response.data

def test_encode():
    """Encoding url test"""
    url = "http://www.foo.com"
    user = User(db=db,email="user@users.com")
    url_encoder = UrlEncoder(url=url)
    long_hash = url_encoder.encode_url(user)
    pattern = '[A-Za-z0-9]+'
    assert re.match(pattern, long_hash)

def test_get_user_id(client):
    """Test getting a users id"""
    user = User(db=db,email='jason@seaver.com')
    actual_user_id = user.get_user_id()
    expected = 1
    assert (expected == actual_user_id)

def test_store_urls(client):
    """Test storing a set of urls"""
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    actual = insert_case(client,urls)
    url_encoder = UrlEncoder(url=urls['desktop'])
    user = User(db=db,email='jason@seaver.com')
    expected =  url_encoder.encode_url(user)[:7]
    assert (expected in actual['data'][0]['shortie'])

def test_redirect_desktop(client):
    """Test that redirect works for desktop user agent"""
    expected = 'https://test.desktop'
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0 (MacOs) AppleWebKit/534.46 (KHTML, like Gecko)'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_mobile(client):
    """Test that redirect works for mobile user agent"""
    expected = 'https://test.mobile'
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'''
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_redirect_tablet(client):
    """Test that redirect works for tablet user agent"""
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    insert_case(client,urls)
    ua_string = '''Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'''
    expected = 'https://test.tablet'
    headers = { 'User-Agent' : ua_string }
    short_url = '/50617f9'
    actual = client.get(short_url,headers=headers).data
    assert (expected in actual)

def test_user_urls(client):
    """Test that the list of urls for a user is returned"""
    urls = { 'desktop' : 'https://test.desktop', 'mobile' : 'https://test.mobile', 'tablet' : 'https://test.tablet'}
    response = insert_case(client,urls)
    short_url = response['data'][0]['shortie']
    request_redirect(client,short_url)
    request_redirect(client,short_url)
    request_redirect(client,short_url)
    user = User(db=db,email='jason@seaver.com')
    rows = user.list_urls()
    assert (len(rows) > 0)
    for row in rows:
        assert (row['url'])
        assert (row['url_type'] and re.match("mobile|tablet|desktop",row['url_type']))
        assert (row['visits'] and row['visits'] == 3)
        assert (row['since'])

def insert_case(tclient,urls):
    """helper function to populate the db with a test case"""
    payload = json.dumps({ 'urls' : urls })
    response = tclient.post('/api/v1/users/jason@seaver.com/urls', data=payload, content_type = 'application/json')
    actual = json.loads(response.data)
    return actual

def request_redirect(tclient,short_url):
    """helper function to add redirect to visits table"""
    ua_string = '''Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'''
    headers = { 'User-Agent' : ua_string }
    actual = tclient.get(short_url,headers=headers).data
