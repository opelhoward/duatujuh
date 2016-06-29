from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector

if __name__ == "__main__":
    db = CsvProductDbConnector("classifier/data/olx.csv")
    all_data = db.all_data()
    all_data = all_data.loc[~(all_data.product_name.isnull() & all_data.description.isnull())]

    label = [x+", sub:"+y for x, y in all_data[['category', 'subcategory']].values]
    data_train, data_test = train_test_split(all_data, stratify=label, train_size=30000, test_size=20000, random_state=71)

    print '############ Start Testing ##########'
    product_classifier = ProductCategoryClassifier()
    product_classifier.build_model_from_data(data_train)

    description = data_test.description
    product_name = data_test.product_name

    print 'Start classify for testing'
    y_pred = product_classifier.classify(zip(data_test.product_name, data_test.description))
    y_pred = [product_classifier._category_tuple_string(x) for x in y_pred]
    y_true = [product_classifier._category_tuple_string(tuple(x)) for x in data_test[['category', 'subcategory']].values]
    print '############# TEST RESULT #############'
    print 'Accuracy Score'
    print accuracy_score(y_true=y_true, y_pred=y_pred)
    print 'F1 Score'
    print f1_score(y_true=y_true, y_pred=y_pred, average='macro')
    print 'Precision Score'
    print precision_score(y_true=y_true, y_pred=y_pred, average='macro')
    print 'Recall Score'
    print recall_score(y_true=y_true, y_pred=y_pred, average='macro')
    print '#######################################'