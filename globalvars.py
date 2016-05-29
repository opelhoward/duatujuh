from classifier.product_classifier import ProductCategoryClassifier


def init(path):
    global cls
    cls = ProductCategoryClassifier()
    cls.load_model(path)
