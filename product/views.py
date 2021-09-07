from typing import Union

import bson
from flask import Blueprint, render_template, redirect, url_for
from werkzeug import Response

from app.view import redirect_to_404_if_not_found
from product.models import Product

bp = Blueprint("product", __name__, template_folder='templates')


@bp.route("/products/")
def product_list() -> str:
    return render_template('product_list.html', products_list=Product.objects()[:10])


@bp.route("/products/<id:product_id>")
@redirect_to_404_if_not_found
def product_detail(product_id: bson.ObjectId) -> Union[str, Response]:
    product = Product.objects.get(pk=product_id)
    return render_template('product_detail.html',
                           product=product)


@bp.route("/products/<id:product_id>/delete", methods=['GET'])
def product_delete(product_id: bson.ObjectId) -> Response:
    product = Product.objects.get(pk=product_id)
    product.delete()
    return redirect(url_for('product.product_list'))
