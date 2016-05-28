import json

from flask import Flask
from flask.ext.script import Manager

from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector
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
@manager.option("-mp", "--model-path", help="Model path", default=None)
def insert_to_db(path, company, model_path):
    classifier = None
    if model_path is not None:
        classifier = ProductCategoryClassifier()
        classifier.load_model(model_path)
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
                if classifier is not None:
                    (category, subcategory) = classifier.classify([(product_json['category'], product_json['subcategory'])])[0]
                    product_json['category'] = category
                    product_json['subcategory'] = subcategory
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


@manager.option("-tp", "--training-path", help="Path to training data")
@manager.option("-mp", "--model-path", help="Path to model")
def create_learning_model(training_path, model_path):
    print("Preparing to learn")
    classifier = ProductCategoryClassifier()
    db = CsvProductDbConnector(training_path)
    classifier.build_model_from_data(db.sample_data(10000))
    classifier.save_model(model_path)
    print("Finish creating model")


@manager.command
def runserver():
    app.register_blueprint(routes.app)
    app.run(debug=True)


if __name__ == '__main__':
    manager.run()
