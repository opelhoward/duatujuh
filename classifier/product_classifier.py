import re
import time
from HTMLParser import HTMLParser

from py4j.java_gateway import JavaGateway
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.naive_bayes import MultinomialNB
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


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
        self._stopwords = self._get_stopwords('classifier/stopwords2.txt')
        self._gateway = JavaGateway()

    def build_model_from_data(self, product_data):
        t0 = time.time()

        data = product_data.copy()

        print 'Removing HTML tags...'
        data.description = data.description.apply(strip_tags)

        print 'Text formalization...'
        # data.description = [self._gateway.formalizeSentence(x) for x in data.description]
        # data.product_name = [self._gateway.formalizeSentence(x) for x in data.product_name]

        print 'Only alphabet...'
        data.description = [re.sub("[^a-zA-Z]", " ", x) for x in data.description]
        data.product_name = [re.sub("[^a-zA-Z]", " ", x) for x in data.product_name]

        product_text = [x+'. '+y for x, y in zip(data.product_name, data.description)]

        print 'Indexing categories...'
        self._initialize_string_cat_converter(data)

        label = [self._category_tuple_string((x, y)) for x, y in data[['category', 'subcategory']].values]

        print 'Create document term matrix...'
        # self._count_vect = TfidfVectorizer(ngram_range=(1, 2),
        #                                    max_features=None,
        #                                    vocabulary=None,
        #                                    binary=False,
        #                                    min_df=4,
        #                                    max_df=0.1,
        #                                    sublinear_tf=True,
        #                                    stop_words=self._stopwords)
        self._count_vect = TfidfVectorizer(ngram_range=(1, 2),
                                           use_idf=True,
                                           sublinear_tf=False,
                                           min_df=2,
                                           max_df=0.15,
                                           stop_words=self._stopwords)

        dtm = self._count_vect.fit_transform(product_text)
        print 'DTM size ' + str(dtm.get_shape())

        print 'Create model...'
        self._model = svm.LinearSVC(C=1,
                                    random_state=71)
        # self._model = RandomForestClassifier(n_estimators=100,
        #                                      min_samples_leaf=5,
        #                                      random_state=3)
        # self._model = MultinomialNB(alpha=0.0009765625)
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
        # product_description = [self._gateway.formalizeSentence(x) for x in product_description]
        # product_name = [self._gateway.formalizeSentence(x) for x in product_name]

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
    def _replace_none_with_value(value, value_if_none):
        if value is None:
            return value_if_none
        else:
            return value




