import math

from ranker import Ranker
from nltk.corpus import wordnet
import nltk
nltk.download('wordnet')

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

    def relevant_docs_from_posting(self, query_word_count, k = None):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        worst_word = (None, math.inf)
        for term, appearance in query_word_count.items():
            try:
                if term.lower() in self._indexer.postingDict:
                    term=term.lower()
                else:
                    term=term.upper()
                dic_value = len(self._indexer.postingDict[term][1])  # [1,[]]
                if worst_word[0]==None or self._indexer.postingDict[term][0]/dic_value > self._indexer.postingDict[worst_word[0]][0]/worst_word[1]:
                    worst_word = (term, dic_value)
            except:
                continue
        if worst_word[0] == None:
            return []
        new_word = self.get_best_synset(worst_word[0])
        #divider = (len(self._indexer.postingDict[new_word][1])/self._indexer.postingDict[new_word][0])/\
        #          (len(self._indexer.postingDict[worst_word[0]][1])/self._indexer.postingDict[worst_word[0]][0])
        num_of_appear = query_word_count[worst_word[0]]
        #query_word_count[worst_word[0]] = num_of_appear/divider
        # del query_word_count[worst_word[0]]
        query_word_count[new_word] = num_of_appear
        return self._ranker.get_relvant_docs(query_word_count, self._indexer.postingDict, self.number_of_documents, k)

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
                if lem in self._indexer.postingDict and len(self._indexer.postingDict[lem][1])/self._indexer.postingDict[lem][0] < best_appear:
                   # best_appear = len(self._indexer.postingDict[lem][1])
                    best_appear = len(self._indexer.postingDict[lem][1])/self._indexer.postingDict[lem][0]
                    best_term = lem
        return best_term

