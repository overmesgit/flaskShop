import os
from http import HTTPStatus
from pathlib import Path
from typing import Union

from flask import Blueprint, render_template, request, redirect, url_for, Response, current_app
from flask_mongoengine.wtf import model_form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from mongoengine import DoesNotExist
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from product.models import Product

bp = Blueprint("product", __name__, template_folder='templates')


@bp.route("/products/")
def product_list() -> str:
    return render_template('product_list.html', products_list=Product.objects()[:10])


@bp.route("/products/<id:product_id>")
def product_detail(product_id) -> Union[str, Response]:
    try:
        product = Product.objects.get(pk=product_id)
    except DoesNotExist:
        return redirect(url_for('product.product_list'))
    else:
        return render_template('product_detail.html',
                               product=product)


class ProductForm(model_form(Product)):
    image = FileField(validators=[
        FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

    def save(self):
        # TODO: it works with instance
        product = Product(
            title=self.title.data,
            image='',
            description=self.description.data,
            price=self.price.data,
            category=self.category.data,
        )
        product.save()
        f = self.image.data
        filename = f'{product.id}_{secure_filename(f.filename)}'
        f.save(Path(current_app.config['UPLOAD_FOLDER']) / filename)

        product.image = filename
        product.save()

        return product


@bp.route("/products/add", methods=['GET', 'POST'])
def product_add() -> Union[str, Response, tuple[str, int]]:
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        if form.validate():
            form.save()
            return redirect(url_for('product.product_list'))
        else:
            resp_body = render_template('product_add.html', form=form)
            return resp_body, HTTPStatus.BAD_REQUEST
    else:
        return render_template('product_add.html', form=form)


@bp.route("/products/<id:product_id>/delete", methods=['GET'])
def product_delete(product_id) -> Response:
    try:
        product = Product.objects.get(pk=product_id)
    except DoesNotExist:
        return redirect(url_for('product.product_list'))
    else:
        product.delete()
        return redirect(url_for('product.product_list'))
