from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from user.model import User

bp = Blueprint("user", __name__, template_folder='templates')


class Login(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    login = SubmitField('Login')


class Register(Login):
    username = StringField(validators=[DataRequired()])


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
            flash('You were successfully logged in.')
            return redirect(url_for('product.product_list'))
        else:
            flash('Wrong user or password.')
    return render_template('login.html', form=form)
