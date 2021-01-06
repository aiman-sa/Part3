import math

from parser_module import Parse
from ranker import Ranker
import utils
from nltk.corpus import wordnet
import nltk
nltk.download('wordnet')
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

    def get_best_synset(self,term):
        if term.lower() in self._indexer.postingDict:
            best_appear =  len(self._indexer.postingDict[term.lower()][1])
        elif term.upper() in self._indexer.postingDict:
            best_appear =  len(self._indexer.postingDict[term.upper()][1])
        else:
            return (None,0)
        best_term = term
        for synset in wordnet.synsets(term):
            for lemma in synset.lemmas():
                lem = lemma.name()
                if lem in self._indexer.postingDict and len(self._indexer.postingDict[lem][1]) > best_appear:
                    best_appear = len(self._indexer.postingDict[lem][1])
                    best_term = lem
        return best_term

    def relevant_docs_from_posting(self, query,k=None):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        query_word_count = {}
        self._parser.tokenSplit(query, query_word_count)
        # relavant_doc_dict = self._ranker.get_relvant_docs(query_word_count,self._indexer.postingDict)
        # for term,
        # todo : need to run ranker on all and check if word have more corrleation with doc , if true chang it
        worst_word = (None, math.inf)
        for term, appearance in query_word_count.items():
            try:
                dic_value = len(self._indexer.postingDict[term][1]) #[1,[]]
                if dic_value < worst_word[1]:
                    worst_word = (term,dic_value)
            except:
                print()
        if worst_word[0]==None:
            return []
        num_of_appear=query_word_count[worst_word[0]]
        del query_word_count[worst_word[0]]
        new_word = self.get_best_synset(worst_word[0])
        query_word_count[new_word] = num_of_appear
        return self._ranker.get_relvant_docs(query_word_count,self._indexer.postingDict,self.number_of_documents,k)

        # DO NOT MODIFY THIS SIGNATURE
        # You can change the internal implementation as you see fit.
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