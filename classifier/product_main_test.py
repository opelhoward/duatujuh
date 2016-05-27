from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector

if __name__ == "__main__":
    db = CsvProductDbConnector("data/olx.csv")

    product_classifier = ProductCategoryClassifier()
    product_classifier.build_model_from_database(db)
    product_description = ['Anting anting untuk perempuan', 'Ban bekas serap goodyear', 'handphone xiomi redmi 3 pro']
    prediction = product_classifier.classify(None, product_description)
    print prediction
