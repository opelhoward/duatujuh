from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pasang-iklan')
def add_ads():
    return render_template('add-ads.html')


@app.route('/daftar-produk')
def list_products():
    return render_template('product-list.html')


@app.route('/deskripsiProduk')
def get_product_desc():
    return render_template('product-desc.html')


if __name__ == '__main__':
    app.run(debug=True)
