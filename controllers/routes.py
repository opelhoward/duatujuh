from flask import Blueprint, render_template

app = Blueprint("routes", __name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pasang-iklan")
def add_ads():
    return render_template("add-ads.html")


@app.route("/daftar-produk")
def list_products():
    return render_template("product-list.html")


@app.route("/product/<product_name>")
def get_product_desc(product_name):
    return render_template("product-desc.html")
