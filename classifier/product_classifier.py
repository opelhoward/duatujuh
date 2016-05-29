import numpy as np
import re
from HTMLParser import HTMLParser

import time
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from py4j.java_gateway import JavaGateway


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# Classifier
class ProductCategoryClassifier:

    def __init__(self):
        self._count_vect = None
        self._model = None
        self._cat_subcat_separator = ', sub:'
        self._string_cat_dict = None
        self._stopwords = self._get_stopwords('stopwords.txt')
        self._gateway = JavaGateway()

    def build_model_from_data(self, product_data):
        t0 = time.time()

        data = product_data.copy()
        print 'Replace NA values...'
        data.description = data.description.fillna('')
        data.product_name = data.product_name.fillna('')

        print 'Removing HTML tags...'
        data.description = data.description.apply(strip_tags)

        print 'Text formalization...'
        data.description = [self._gateway.formalizeSentence(x) for x in data.description]
        data.product_name = [self._gateway.formalizeSentence(x) for x in data.product_name]

        print 'Only alphabet...'
        data.description = [re.sub("[^a-zA-Z]", " ", x) for x in data.description]
        data.product_name = [re.sub("[^a-zA-Z]", " ", x) for x in data.product_name]

        print 'Indexing categories...'
        self._initialize_string_cat_converter(data)

        label = [self._category_tuple_string((x, y)) for x, y in data[['category', 'subcategory']].values]

        print 'Create document term matrix...'
        self._count_vect = TfidfVectorizer(ngram_range=(1, 2),
                                           max_features=None,
                                           vocabulary=None,
                                           binary=False,
                                           min_df=4,
                                           max_df=0.1,
                                           sublinear_tf=True,
                                           stop_words=self._stopwords)
        dtm = self._count_vect.fit_transform(data.description)
        print 'DTM size ' + str(dtm.get_shape())

        print 'Create model...'
        self._model = svm.LinearSVC(C=0.5,
                                    class_weight='balanced',
                                    random_state=71,
                                    dual=True)
        self._model.fit(dtm, label)
        t1 = time.time()
        print 'Model created in ' + str(t1-t0)

    def classify(self, product_name_description_tupple):
        print 'Replace missing value with empty string...'
        product_description = [self._replace_none_with_value(x[1], '') for x in product_name_description_tupple]
        product_name = [self._replace_none_with_value(x[0], '') for x in product_name_description_tupple]

        print 'Removing unknown instance HTML tags...'
        product_description = [strip_tags(x) for x in product_description]

        print 'Text formalization...'
        product_description = [self._gateway.formalizeSentence(x) for x in product_description]
        product_name = [self._gateway.formalizeSentence(x) for x in product_name]

        print 'Only alphabet'
        product_description = [re.sub("[^a-zA-Z]", " ", x) for x in product_description]
        product_name = [re.sub("[^a-zA-Z]", " ", x) for x in product_name]

        product_text = [x+'. '+y for x, y in zip(product_name, product_description)]

        print 'Building document term matrix...'
        dtm = self._count_vect.transform(product_text)

        print 'Start predicting..'
        prediction = self._model.predict(dtm)
        return [self._category_string_tuple(x) for x in prediction]

    def save_model(self, model_path):
        print 'Saving model...'
        persistent_dict = {'model': self._model, 'count_vect': self._count_vect,
                           'string_cat_dict': self._string_cat_dict}
        joblib.dump(persistent_dict, model_path)
        print 'Saved.'

    def load_model(self, model_path):
        print 'Loading model...'
        persistent_dict = joblib.load(model_path)
        self._model = persistent_dict['model']
        self._count_vect = persistent_dict['count_vect']
        self._string_cat_dict = persistent_dict['string_cat_dict']
        print 'Loaded.'

    def build_model_and_performance_testing(self, product_data):

        label = [self._category_tuple_string((x, y)) for x, y in product_data[['category', 'subcategory']].values]
        data_train, data_test = train_test_split(product_data, stratify=label, test_size=0.3, random_state=71)
        self.build_model_from_data(data_train)

        description = data_test.description.fillna('')
        product_name = data_test.product_name.fillna('')

        print 'Start classify for testing'
        y_pred = self.classify(zip(product_name, description))
        y_pred = [self._category_tuple_string(x) for x in y_pred]
        y_true = [self._category_tuple_string(tuple(x)) for x in data_test[['category', 'subcategory']].values]
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

    def _initialize_string_cat_converter(self, data):
        full_category = data[['category', 'subcategory']]
        full_category_tuple = set([tuple(x) for x in full_category.values])
        full_category_names = [x+self._cat_subcat_separator+y for x, y in full_category_tuple]
        self._string_cat_dict = dict(zip(full_category_names, full_category_tuple))

    def _category_tuple_string(self, category_subcategory):
        x, y = category_subcategory
        return x+self._cat_subcat_separator+y

    def _category_string_tuple(self, category_string):
        return self._string_cat_dict[category_string]

    @staticmethod
    def _get_stopwords(file_path):
        stopwords = []
        with open(file_path, "r") as input_file:
            for line in input_file:
                stopwords.append(line.rstrip())
        return stopwords

    @staticmethod
    def __feature_selection(product_text, target):
        count_vectorizer = TfidfVectorizer(ngram_range=(1, 2),
                                           max_features=None,
                                           vocabulary=None,
                                           binary=False,
                                           min_df=2,
                                           max_df=0.1,
                                           sublinear_tf=True)
        dtm = count_vectorizer.fit_transform(product_text)
        print 'DTM size ' + str(dtm.get_shape())

        clf = ExtraTreesClassifier(n_estimators=50, random_state=71)
        clf = clf.fit(dtm, target)
        select_model = SelectFromModel(clf, prefit=True)

        selected_feature = select_model.get_support()
        selected_vocab = np.asarray(count_vectorizer.get_feature_names())[selected_feature]
        return selected_vocab

    @staticmethod
    def _replace_none_with_value(value, value_if_none):
        if value is None:
            return value_if_none
        else:
            return value




