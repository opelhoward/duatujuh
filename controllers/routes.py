import math
from flask import Blueprint, render_template, request

from models.productmodel import Product

app = Blueprint("routes", __name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pasang-iklan")
def add_ads():
    return render_template("add-ads.html")


NUMBER_OF_ITEMS_IN_PAGE = 24


@app.route("/category/<category_name>")
def list_products(category_name):
    page_number = request.args.get('page')
    if page_number is None:
        page_number = 1
    products_pagination = Product.query \
        .filter_by(category=" " + category_name) \
        .paginate(page_number, NUMBER_OF_ITEMS_IN_PAGE)
    products = products_pagination.items
    number_of_products = products_pagination.total
    number_of_pages = int(math.ceil(number_of_products / NUMBER_OF_ITEMS_IN_PAGE))
    pagination_start = max(page_number - 3, 1)
    pagination_end = min(number_of_pages, pagination_start + 6)
    return render_template("product-list.html",
                           category=category_name,
                           products=products,
                           number_of_pages=number_of_pages,
                           curr_page_num=page_number,
                           pagination_start=pagination_start,
                           pagination_end=pagination_end
                           )


@app.route("/product/<product_id>")
def get_product_desc(product_id):
    return render_template("product-desc.html")


@app.route('/admin')
def get_admin():
    return render_template('admin.html')
