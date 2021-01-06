import math

from parser_module import Parse
from ranker import Ranker
import utils
from nltk.corpus import wordnet

class Searcher:

    def __init__(self, parser, indexer, model=None):
        #lalala
        """
        :param inverted_index: dictionary of inverted index
        """
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.number_of_documents=0

    def get_replacement(self, term):
        if term.lower() in self._indexer.postingDict:
            term=term.lower()
        elif term.upper() in self._indexer.postingDict:
            term=term.upper()
        else:
            term=None
        new_word = self._indexer.spell_correction(term)
        key_set = self._indexer.postingDict
        return_word = term
        if new_word in key_set:
            if term==None or len(self._indexer.postingDict[new_word][1]) > len(self._indexer.postingDict[term]):
                return_word = new_word

        return return_word

    def relevant_docs_from_posting(self, query, k=None):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        query_word_count = {}
        self._parser.tokenSplit(query, query_word_count)
        best_qurey_word_dict = {}
        for term, value in query_word_count.items():
            try:
                word = self.get_replacement(term)
                if word != None:
                    best_qurey_word_dict[word] = value
            except:
                print('term {} not found in posting'.format(term))
        return self._ranker.get_relvant_docs(query_word_count, self._indexer.postingDict,self.number_of_documents,k)


    def search(self, query, k=None):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        relevant_docs = self.relevant_docs_from_posting(query,k)
        n_relevant = len(relevant_docs)
        #ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, relevant_docs