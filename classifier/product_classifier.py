from HTMLParser import HTMLParser

from sklearn import svm
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer


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

    def build_model_from_database(self, product_database):
        data = product_database.sample_data(10000)
        print 'Replace NA values...'
        data.description = data.description.fillna('')

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
        dtm = self._count_vect.transform(product_description)
        prediction = self._model.predict(dtm)
        return [self._category_string_tuple(x) for x in prediction]

    def save_model(self, model_path):
        persistent_dict = {'model': self._model, 'count_vect': self._count_vect}
        joblib.dump(persistent_dict, model_path)

    def load_model(self, model_path):
        persistent_dict = joblib.load(model_path)
        self._model = persistent_dict['model']
        self._count_vect = persistent_dict['count_vect']

    def performance_testing(self):
        pass

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




