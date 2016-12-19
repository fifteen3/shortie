import pytest
from shortie import api

@pytest.fixture
def client():
    client = api.app.test_client()
    return client

def test_root(client):
    response = client.get('/')
    assert u'Welcome to Shortie.' in response.data
