import random

import pandas as pd


class CsvProductDbConnector:

    def __init__(self, file_path):
        self.file_path = file_path
        print 'Start loading data...'
        self.data = pd.read_csv(self.file_path)
        print 'Finish loading data.'

    def all_data(self):
        return self.data

    def sample_data(self, n):
        print 'Sampling data...'
        return self.data.sample(n, random_state=71)
