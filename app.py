from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/pasangIklan')
def pasangIklan():
    return render_template('pasangIklan.html')

@app.route('/produkList')
def produkList():
    return render_template('produkList.html')

@app.route('/deskripsiProduk')
def deskripsiProduk():
    return render_template('deskripsiProduk.html')

@app.route('/deskripsiEcommerce')
def deskripsiEcommerce():
    return render_template('deskripsiEcommerce.html')

@app.route('/adminPage')
def adminPage():
    return render_template('adminPage.html')

if __name__ == '__main__':
    app.run(debug=True)
