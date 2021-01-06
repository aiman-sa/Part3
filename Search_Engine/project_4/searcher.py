from parser_module import Parse
from ranker import Ranker
import utils

class Searcher:

    def __init__(self, parser, indexer, model=None):
        """
        :param inverted_index: dictionary of inverted index
        """
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.number_of_documents=0

    def relevant_docs_from_posting(self, query, k = None):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        return self._ranker.get_relvant_docs(query, self._indexer.postingDict, self.number_of_documents, k)


