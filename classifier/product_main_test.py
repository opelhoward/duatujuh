from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector

if __name__ == "__main__":
    db = CsvProductDbConnector("classifier/data/olx.csv")

    product_classifier = ProductCategoryClassifier()
    product_classifier.build_model_and_performance_testing(db.sample_data(50000).fillna(''))

    product_text = [('Anting anting untuk perempuan', 'Aksesoris ini dapat membuat anda tampil lebih cantik'),
                    ('Ban bekas serap goodyear', 'ban ini sangat awet dan tahan lama'),
                    ('handphone xiomi redmi 3 pro', 'ram 3gb dan rom 9gb')]
    prediction = product_classifier.classify(product_text)
    print prediction
