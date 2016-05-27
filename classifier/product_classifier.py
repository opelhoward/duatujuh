import random
from HTMLParser import HTMLParser
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, accuracy_score, f1_score, recall_score, precision_score


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

    def build_model_from_data(self, product_data):
        data = product_data.copy()
        print 'Replace NA values...'
        data.description = data.description.fillna('')
        data.product_name = data.product_name.fillna('')

        print 'Indexing categories...'
        self._initialize_string_cat_converter(data)

        print 'Create document term matrix...'
        self._count_vect = CountVectorizer(ngram_range=(1, 1),
                                           max_features=1000,
                                           vocabulary=None,
                                           binary=False,
                                           min_df=2)
        dtm = self._count_vect.fit_transform(data.description)

        print 'Create model...'
        label = [self._category_tuple_string((x, y)) for x, y in data[['category', 'subcategory']].values]
        self._model = svm.SVC(C=1.0, kernel='linear')
        self._model.fit(dtm, label)

    def classify(self, product_name, product_description):
        print 'Replace missing value with empty string...'
        product_description = [self._replace_none_with_value(x, '') for x in product_description]
        product_name = [self._replace_none_with_value(x, '') for x in product_name]

        print 'Building document term matrix...'
        dtm = self._count_vect.transform(product_description)

        print 'Start predicting..'
        prediction = self._model.predict(dtm)
        return [self._category_string_tuple(x) for x in prediction]

    def save_model(self, model_path):
        print 'Saving model...'
        persistent_dict = {'model': self._model, 'count_vect': self._count_vect}
        joblib.dump(persistent_dict, model_path)
        print 'Saved.'

    def load_model(self, model_path):
        print 'Loading model...'
        persistent_dict = joblib.load(model_path)
        self._model = persistent_dict['model']
        self._count_vect = persistent_dict['count_vect']
        print 'Loaded.'

    def build_model_and_performance_testing(self, product_data):
        random.seed(1)

        label = [self._category_tuple_string((x, y)) for x, y in product_data[['category', 'subcategory']].values]
        data_train, data_test = train_test_split(product_data, stratify=label, test_size=0.3)
        self.build_model_from_data(data_train)

        description = data_test.description.fillna('')
        product_name = data_test.product_name.fillna('')

        print 'Start classify for testing'
        y_pred = self.classify(product_name, description)
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
    def _replace_none_with_value(value, value_if_none):
        if value is None:
            return value_if_none
        else:
            return value




