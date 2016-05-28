import json

from flask import Flask
from flask.ext.script import Manager

from controllers import routes
from models import db
from models.productmodel import Product

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

manager = Manager(app)


@manager.command
def create_db():
    with app.app_context():
        db.create_all()
    print("Finish creating table(s)")


@manager.option("-p", "--path", help="JSON file path")
@manager.option("-c", "--company", help="Company name")
def insert_to_db(path, company):
    with app.app_context():
        objects = list()
        print("Preparing to open %s" % path)
        with open(path) as data_file:
            product_arr = json.load(data_file)
            count = 0
            for product_json in product_arr:
                if product_json['product_name'] is None:
                    continue
                count += 1
                print("Adding product %d out of %d" % (count, len(product_arr)))
                product = Product(company=company, **product_json)
                objects.append(product)
                if len(objects) is 100:
                    db.session.bulk_save_objects(objects)
                    db.session.commit()
                    objects = list()
        if len(objects):
            db.session.bulk_save_objects(objects)
            db.session.commit()
        print("Finish adding to database")


@manager.command
def runserver():
    app.register_blueprint(routes.app)
    app.run(debug=True)

if __name__ == '__main__':
    manager.run()
