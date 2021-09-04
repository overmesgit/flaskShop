from flask import Blueprint

bp = Blueprint("product", __name__)


@bp.route("/products/")
def product_list():
    return 'Product list'
