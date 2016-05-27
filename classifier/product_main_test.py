from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector

if __name__ == "__main__":
    db = CsvProductDbConnector("data/olx.csv")

    product_classifier = ProductCategoryClassifier()
    product_classifier.build_model_and_performance_testing(db.sample_data(10000))
    # product_classifier.build_model_from_data(db.sample_data(10000))
    product_description = ['Anting anting untuk perempuan', 'Ban bekas serap goodyear', 'handphone xiomi redmi 3 pro']
    prediction = product_classifier.classify([], product_description)
    print prediction
