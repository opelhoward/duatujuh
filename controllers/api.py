import flask
from flask import Blueprint, request

import globalvars

app = Blueprint("api", __name__, url_prefix="/api")


@app.route("/categorize", methods=["POST"])
def categorize():
    product_name = request.form.get("product_name")
    desc = request.form.get("description")

    classifier = globalvars.cls
    (category, subcategory) = classifier.classify([(product_name, desc)])[0]
    return flask.jsonify({
        "category": category,
        "subcategory": subcategory
    })
