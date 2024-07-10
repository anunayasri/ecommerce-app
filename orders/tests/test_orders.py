import pytest
from api.api import create_app
from config import TestingConfig

@pytest.fixture()
def app():
    app = create_app(TestingConfig)

    # other setup can go here
    print(f"test: before yield")

    yield app

    print(f"test: after yield")

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_get_order_by_id(client):
    resp = client.get('/orders/1')
    assert resp.status_code == 200

    data = resp.json
    assert data['id'] == 1

