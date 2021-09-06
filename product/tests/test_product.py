from http import HTTPStatus

from lxml.html import fromstring

from app.tests.conftest import *
from product.models import Product


def test_products_list(app, client):
    product = Product(title='test', image='https://s3-image-1.png',
                      description='test', price=10,
                      category='test')
    product.save()

    with captured_templates(app) as templates:
        response = client.get('/products/')

        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_list.html'
        assert len(context['products_list']) == 1

        assert product.title.encode() in response.data
        assert f'href="/products/add'.encode() in response.data


def test_products_add(app, client):
    # GET
    Product.objects().delete()
    with captured_templates(app) as templates:
        response = client.get('/products/add')

        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_add.html'
        assert context['form']

        assert f'action="/products/add'.encode() in response.data

    # POST
    lxml_resp = fromstring(response.data)
    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    product_data = dict(
        csrf_token=csrf_token, title='hello',
        image='test', description='test', price=10,
        category='test', )
    response = client.post('/products/add', data=product_data)
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 1
    product: Product = objects[0]
    for k, v in product_data.items():
        if hasattr(product, k):
            assert getattr(product, k) == v

    # DETAIL
    with captured_templates(app) as templates:
        response = client.get(f'/products/{product.id}')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_detail.html'
        assert f'{product.description}'.encode() in response.data
