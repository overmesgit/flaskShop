from flask import Blueprint

from product.model import Product

bp = Blueprint("product", __name__)


@bp.route("/products/")
def product_list() -> str:
    return f'Product list {Product.objects().count()}'
