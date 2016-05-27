from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html', a=1)

@app.route('/pasangIklan')
def pasangIklan():
    return render_template('pasangIklan.html', a=1)

@app.route('/produkList')
def produkList():
    return render_template('produkList.html', a=1)

@app.route('/deskripsiProduk')
def deskripsiProduk():
    return render_template('deskripsiProduk.html', a=1)


if __name__ == '__main__':
    app.run(debug=True)
