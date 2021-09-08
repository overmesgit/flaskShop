from http import HTTPStatus

from flask import session, get_flashed_messages
from flask_login import current_user
from lxml.html import fromstring

from app.tests.conftest import *
from user.model import User
from user.view import UserType


def test_register(app, client):
    with captured_templates(app) as templates:
        response = client.get(f'/register')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'register.html'
        assert context['form']
        lxml_resp = fromstring(response.data)
        form = lxml_resp.cssselect('form')[0]
        assert f'/register' == form.action

    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value
    with client:
        request_data = {
            'username': 'test_user',
            'email': 'a@b.com',
            'password': 'qwer',
            'csrf_token': csrf_token
        }
        response = client.post('/register', data=request_data)
        assert response.status_code == HTTPStatus.FOUND
        user_qs = User.objects(username=request_data['username'])
        assert user_qs
        user = user_qs[0]
        assert user.email == request_data['email']
        assert user.password_hash != request_data['password']
        assert current_user.username == user.username


def test_login(app, client):
    with captured_templates(app) as templates:
        response = client.get(f'/login')

        assert response.status_code == HTTPStatus.OK
        assert len(templates)
        template, context = templates[0]
        assert template.name == 'login.html'
        assert context['form']
        lxml_resp = fromstring(response.data)
        form = lxml_resp.cssselect('form')[0]
        assert f'/login' == form.action

    csrf_token = lxml_resp.cssselect('#csrf_token')[0].value

    # LOGIN
    with client:
        user = User(username='test_login', email='login@a.com', password='asdf')
        user.save()

        client.post('/login', data={
            'email': user.email, 'password': '1' + user.password, 'csrf_token': csrf_token,
            'user_type': UserType.CUSTOMER
        })
        assert 'Wrong' in get_flashed_messages()[0]
        assert current_user.is_anonymous

        response = client.post('/login', data={
            'email': user.email, 'password': user.password, 'csrf_token': csrf_token,
            'user_type': UserType.CUSTOMER
        })
        assert response.status_code == HTTPStatus.FOUND
        assert not current_user.is_anonymous
        assert current_user.username == user.username
        assert session['user_type'] == UserType.CUSTOMER

    # LOGOUT
        response = client.get('/logout')
        assert response.status_code == HTTPStatus.FOUND
        assert current_user.is_anonymous
        assert session['user_type'] == None

        response = client.post('/login', data={
            'email': user.email, 'password': user.password, 'csrf_token': csrf_token,
            'user_type': UserType.SELLER
        })
        assert response.status_code == HTTPStatus.FOUND
        assert not current_user.is_anonymous
        assert current_user.username == user.username
        assert session['user_type'] == UserType.SELLER

    # LOGOUT
        response = client.get('/logout')
        assert response.status_code == HTTPStatus.FOUND
        assert current_user.is_anonymous
        assert session['user_type'] == None

