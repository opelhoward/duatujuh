from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn import cross_validation

from classifier.product_classifier import ProductCategoryClassifier
from classifier.product_database import CsvProductDbConnector

if __name__ == "__main__":
    db = CsvProductDbConnector("classifier/data/olx.csv")
    all_data = db.all_data()
    all_data = all_data.loc[~(all_data.product_name.isnull() & all_data.description.isnull())]

    print all_data.shape[0]
    kf = cross_validation.KFold(n=all_data.shape[0],
                                n_folds=10,
                                shuffle=True,
                                random_state=71)

    product_classifier = ProductCategoryClassifier()
    y_truelist = []
    y_predlist = []
    for train_index, test_index in kf:
        print 'Start fold'
        data_train = all_data.iloc[train_index]
        data_test = all_data.iloc[test_index]

        product_classifier.build_model_from_data(data_train)

        description = data_test.description
        product_name = data_test.product_name

        y_pred = product_classifier.classify(zip(product_name, description))
        y_pred = [product_classifier._category_tuple_string(x) for x in y_pred]
        y_true = [product_classifier._category_tuple_string(tuple(x)) for x in data_test[['category', 'subcategory']].values]

        y_truelist.extend(y_true)
        y_predlist.extend(y_pred)

    print '############# TEST RESULT #############'
    print 'Accuracy Score'
    print accuracy_score(y_true=y_truelist, y_pred=y_predlist)
    print 'F1 Score'
    print f1_score(y_true=y_truelist, y_pred=y_predlist, average='macro')
    print 'Precision Score'
    print precision_score(y_true=y_truelist, y_pred=y_predlist, average='macro')
    print 'Recall Score'
    print recall_score(y_true=y_truelist, y_pred=y_predlist, average='macro')
    print '#######################################'

    category_true = [product_classifier._category_string_tuple(x)[0] for x in y_truelist]
    category_pred = [product_classifier._category_string_tuple(x)[0] for x in y_predlist]
    print '######### TEST RESULT CATEGORY ########'
    print 'Accuracy Score'
    print accuracy_score(y_true=category_true, y_pred=category_pred)
    print 'F1 Score'
    print f1_score(y_true=category_true, y_pred=category_pred, average='macro')
    print 'Precision Score'
    print precision_score(y_true=category_true, y_pred=category_pred, average='macro')
    print 'Recall Score'
    print recall_score(y_true=category_true, y_pred=category_pred, average='macro')
    print '#######################################'

    with open('classifier/data/analysis.csv', 'w') as fl:
        fl.write('true_category,true_subcategory,pred_category,pred_subcategory\n')
        for true, pred in zip(y_truelist, y_predlist):
            temp = product_classifier._category_string_tuple(true)
            fl.write("\""+temp[0]+"\",\""+temp[1]+"\"")
            temp = product_classifier._category_string_tuple(pred)
            fl.write(",\""+temp[0]+"\",\""+temp[1]+"\"\n")


