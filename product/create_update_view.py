import os
from http import HTTPStatus
from pathlib import Path
from typing import Union, Any

import bson
from flask import current_app, request, redirect, url_for, render_template
from flask_mongoengine.wtf import model_form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug import Response
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from wtforms import DecimalField
from wtforms.validators import NumberRange

from product.models import Product
from product.views import bp


class ProductForm(model_form(Product)):  # type: ignore
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    price = DecimalField(validators=[NumberRange(min=0.01)])

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.image.kwargs.append(FileRequired())

    def get_action(self) -> str:
        return url_for('product.product_add_update', product_id=self.instance.pk)

    def save(self, commit: bool = True, **kwargs: dict[str, Any]) -> Product:
        old_image = self.instance.image

        product: Product = super().save(commit=False, **kwargs)
        f = self.image.data
        if f:
            if not product.pk:
                product.image = ''
                product.save()

            filename = f'{product.id}_{secure_filename(f.filename)}'
            f.save(Path(current_app.config['UPLOAD_FOLDER']) / filename)

            product.image = filename
            product.save()

            if old_image and old_image != filename:
                os.remove(Path(current_app.config['UPLOAD_FOLDER']) / old_image)
        else:
            product.image = old_image
            product.save()
        return product


@bp.route("/products/add", methods=['GET', 'POST'])
@bp.route("/products/<id:product_id>/edit", methods=['GET', 'POST'])
def product_add_update(product_id: bson.ObjectId = None) -> Union[str, Response, tuple[str, int]]:
    if product_id:
        product = Product.objects.get(pk=product_id)
    else:
        product = Product()
    form = ProductForm(CombinedMultiDict((request.files, request.form)), instance=product)
    if request.method == 'GET':
        return render_template('product_add_update.html', form=form)
    else:
        if form.validate():
            obj = form.save()
            return redirect(url_for('product.product_detail', product_id=obj.id))
        else:
            resp_body = render_template('product_add_update.html', form=form)
            return resp_body, HTTPStatus.BAD_REQUEST
