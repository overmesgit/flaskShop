from app.tests.conftest import *


def test_products_list(client):
    response = client.get('/products/')
    assert response.data == b'Product list'
