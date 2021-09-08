from flask import Blueprint, redirect, url_for, request, flash, render_template, session
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired

from user.model import User

bp = Blueprint("user", __name__, template_folder='templates')


class UserType:
    CUSTOMER = 'CUSTOMER'
    SELLER = 'SELLER'

    ALL_TYPES = [CUSTOMER, SELLER]


class Login(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    user_type = RadioField(choices=UserType.ALL_TYPES, validators=[DataRequired()])
    login = SubmitField('Login')


class Register(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    register = SubmitField('Register')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('product.product_list'))
    form = Register(request.form)
    if form.validate_on_submit():
        form_data = form.data
        user = User(username=form_data['username'], email=form_data['email'],
                    password=form_data['password']).save()
        login_user(user)
        return redirect(url_for('product.product_list'))

    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('product.product_list'))
    form = Login(request.form)
    if form.validate_on_submit():
        user = User.load_user(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            session['user_type'] = form.user_type.data
            flash('You were successfully logged in.')
            return redirect(url_for('product.product_list'))
        else:
            flash('Wrong user or password.')
    return render_template('login.html', form=form)


@bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        session['user_type'] = None
        logout_user()
    return redirect(url_for('product.product_list'))