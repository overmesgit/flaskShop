import io
from http import HTTPStatus
from pathlib import Path

from PIL import Image
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


def test_products_crud(app, client):
    # CREATE FORM
    Product.objects().delete()
    with captured_templates(app) as templates:
        response = client.get('/products/add')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_add_update.html'
        assert context['form']
        lxml_resp = fromstring(response.data)

        form = lxml_resp.cssselect('form')[0]
        assert f'/products/add' == form.action

    # CREATE
    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    im = Image.new("RGB", (1, 1), "#FF0000")
    product_data = dict(
        csrf_token=csrf_token, title='hello',
        image=(io.BytesIO(im.tobytes()), 'test.jpg'),
        description='test', price=10,
        category='test')
    response = client.post('/products/add', data=product_data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 1
    product: Product = objects[0]
    assert f'/products/{product.pk}' in response.location

    for k in ['title', 'description', 'price', 'category']:
        assert getattr(product, k) == product_data[k]
    assert product.image == f'{product.id}_{product_data["image"][1]}'
    expected_path = Path(app.config['UPLOAD_FOLDER']) / product.image
    assert open(expected_path, 'rb').read() == im.tobytes()

    # DETAIL
    with captured_templates(app) as templates:
        response = client.get(f'/products/{product.id}')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_detail.html'
        assert f'{product.description}'.encode() in response.data

    # DELETE
    response = client.get(f'/products/{product.id}/delete')
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 0


@pytest.fixture
def product(client) -> Product:
    Product.objects().delete()
    response = client.get('/products/add')
    assert response.status_code == HTTPStatus.OK
    lxml_resp = fromstring(response.data)
    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    im = Image.new("RGB", (1, 1), "#FF0000")
    product_data = dict(
        csrf_token=csrf_token, title='hello',
        image=(io.BytesIO(im.tobytes()), 'test.jpg'),
        description='test', price=10,
        category='test')
    response = client.post('/products/add', data=product_data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 1
    product: Product = objects[0]
    return product


def test_products_update(app, client, product):
    # EDIT FORM
    with captured_templates(app) as templates:
        response = client.get(f'/products/{product.pk}/edit')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_add_update.html'
        assert context['form']
        lxml_resp = fromstring(response.data)
        form = lxml_resp.cssselect('form')[0]
        assert f'/products/{product.pk}/edit' == form.action

    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    # EDIT SAVE
    new_im = Image.new("RGB", (2, 2), "#FF0000")
    new_product_data = dict(
        csrf_token=csrf_token, title='hello1',
        image=(io.BytesIO(new_im.tobytes()), 'test1.jpg'),
        description='test1', price=11,
        category='test1')
    response = client.post(f'/products/{product.pk}/edit', data=new_product_data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 1
    updated_product: Product = objects[0]
    assert f'/products/{updated_product.pk}' in response.location

    expected_path = Path(app.config['UPLOAD_FOLDER']) / product.image
    assert not os.path.exists(expected_path)

    for k in ['title', 'description', 'price', 'category']:
        assert getattr(updated_product, k) == new_product_data[k]
    assert updated_product.image == f'{updated_product.id}_{new_product_data["image"][1]}'
    expected_path = Path(app.config['UPLOAD_FOLDER']) / updated_product.image
    assert open(expected_path, 'rb').read() == new_im.tobytes()


def test_products_update_without_file_change(app, client, product):
    # EDIT FORM
    with captured_templates(app) as templates:
        response = client.get(f'/products/{product.pk}/edit')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'product_add_update.html'
        assert context['form']
        lxml_resp = fromstring(response.data)
        form = lxml_resp.cssselect('form')[0]
        assert f'/products/{product.pk}/edit' == form.action

    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    # EDIT SAVE
    new_product_data = dict(
        csrf_token=csrf_token, title='hello1',
        description='test1', price=11, image='',
        category='test1')
    response = client.post(f'/products/{product.pk}/edit', data=new_product_data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.FOUND
    objects = Product.objects()
    assert objects.count() == 1
    updated_product: Product = objects[0]
    assert f'/products/{updated_product.pk}' in response.location

    expected_path = Path(app.config['UPLOAD_FOLDER']) / product.image
    assert os.path.exists(expected_path)

    for k in ['title', 'description', 'price', 'category']:
        assert getattr(updated_product, k) == new_product_data[k]
    assert product.image == updated_product.image


# all should fail
@pytest.mark.parametrize("field,value", [
    ('title', ''),
    ('description', ''),
    ('price', 0),
    ('image', (io.BytesIO(Image.new("RGB", (1, 1), "#FF0000").tobytes()), 'test1.txt')),
    ('category', ''),
])
def test_products_show_error(app, client, product, field, value):
    app.config.setdefault('WTF_CSRF_ENABLED', False)
    # EDIT SAVE
    new_product_data = dict(
        title='hello1',
        description='test1', price=10, image='',
        category='test1')
    new_product_data[field] = value
    response = client.post(f'/products/{product.pk}/edit', data=new_product_data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    lxml_resp = fromstring(response.data)
    field = lxml_resp.cssselect(f'label[for="{field}"]')[0].getparent().getparent()
    assert field.cssselect('.is-danger')
