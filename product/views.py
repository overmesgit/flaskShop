from http import HTTPStatus
from typing import Union

from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask_mongoengine.wtf import model_form

from product.models import Product

bp = Blueprint("product", __name__, template_folder='templates')


@bp.route("/products/")
def product_list() -> str:
    return render_template('product_list.html', products_list=Product.objects()[:10])


@bp.route("/products/<string:product_id>")
def product_detail(product_id) -> Union[str, Response]:
    try:
        product = Product.objects.get(pk=product_id)
    except Exception:
        return redirect(url_for('product.product_list'))
    else:
        return render_template('product_detail.html',
                               product=product)


class ProductForm(model_form(Product)):
    def save(self):
        product = Product(
            title=self.title.data,
            image=self.image.data,
            description=self.description.data,
            price=self.price.data,
            category=self.category.data,
        )
        product.save()
        return product


@bp.route("/products/add", methods=['GET', 'POST'])
def product_add() -> Union[str, Response, tuple[str, int]]:
    form = ProductForm(request.form)
    if request.method == 'POST':
        if form.validate():
            form.save()
            return redirect(url_for('product.product_list'))
        else:
            resp_body = render_template('product_add.html', form=form)
            return resp_body, HTTPStatus.BAD_REQUEST
    else:
        return render_template('product_add.html', form=form)
