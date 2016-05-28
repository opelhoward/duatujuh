import json
import math
import random

import numpy
from flask import Blueprint, render_template, request, session

from classifier.product_classifier import ProductCategoryClassifier
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
    product = Product.query.get_or_404(product_id)

    view_path_file = None
    if product.company is "MyCompany":
        view_path_file = "product-desc.html"
    else:
        view_path_file = "ecommerce-desc.html"
    return render_template(view_path_file, product=product)


@app.route('/admin')
def get_admin():
    limit = 100
    product_arr = list()
    with open("scraper/scrapeddata/tokopedia.json") as json_file:
        tokopedia_products = json.load(json_file)
        random.seed(1)
        sample_idx_list = numpy.random.choice(range(len(tokopedia_products)), size=limit, replace=False)
        for sample_idx in sample_idx_list:
            product_json = tokopedia_products[sample_idx]
            product_arr.append(product_json)
            product_json['id'] = len(product_arr)
        session["sample_indices"] = sample_idx_list.tolist()
    return render_template('admin.html', products=product_arr)


@app.route("/admin/result")
def get_admin_result():
    sample_indices = session.pop("sample_indices", None)
    if sample_indices is None:
        return get_admin()
    classified_product_arr = list()
    classifier = ProductCategoryClassifier()
    classifier.load_model("classifier/data/pc")
    with open("scraper/scrapeddata/tokopedia.json") as json_file:
        tokopedia_products = json.load(json_file)
        for sample_idx in sample_indices:
            product_json = tokopedia_products[sample_idx]
            (category, subcategory) = classifier.classify([(product_json["product_name"], product_json["description"])])[0]
            product_json["pred_category"] = category
            product_json["pred_subcategory"] = subcategory
            classified_product_arr.append(product_json)
    return render_template("admin-res.html", products=classified_product_arr)
