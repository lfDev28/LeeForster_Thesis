import pytest
from app.routes.smu import smu_connect
from app import create_app as app


@pytest.fixture
def client():
    with app().test_client() as client:
        yield client


def test_smu_connect_route_error(client):
    # Simulate a POST request to the '/connect' route with an invalid port
    response = client.post('/smu/connect', json={"port": 'invalid'})

    # Perform assertions on the response
    assert response.status_code == 500
    assert b'Failed to connect to Smu' in response.data
