from product.model import Product
from app.tests.conftest import *


def test_products_list(client):

    Product(
        title='test',
        images=['test'],
        description='test',
        price=10,
        categories=['test']
    ).save()
    print(Product.objects())
    response = client.get('/products/')
    assert response.data == b'Product list 1'
