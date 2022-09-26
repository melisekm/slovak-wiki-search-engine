import os.path
import pickle


class InvertedIndex:
    def __init__(self, paths):
        self.inverted_index_path = paths.get('inverted_index')
        self.wikipedia_data_path = paths.get('wikipedia_dump_small')
        self._index = None

    def is_loaded(self):
        if self._index is None:
            return False
        return True

    def load(self):
        if os.path.exists(self.inverted_index_path):
            with open(self.inverted_index_path, 'rb') as inverted_index_file:
                self._index = pickle.load(inverted_index_file)
        else:
            self.create()
            self.save()

    def save(self):
        with open(self.inverted_index_path, 'wb') as inverted_index_file:
            pickle.dump(self._index, inverted_index_file)

    def get(self, term):
        if not self.is_loaded():
            raise Exception('Inverted index is not loaded.')
        return self._index.get(term)

    def create(self):
        pass
