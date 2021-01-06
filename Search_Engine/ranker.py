# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math
import operator
import numpy as np
import pandas as pd

class Ranker:
    def __init__(self):
        pass

    def rank_relevant_docs(self,relevant_docs,k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        value=[d[0] for d in ranked_results]
        return value

    def weight_of_term(self,term_frequence, number_of_dcoument_in_compos, number_of_document_with_term,number_of_term_in_document=0):
        _k = 1.2
        _b = 0.75
        idf_term = math.log2(number_of_dcoument_in_compos / number_of_document_with_term)
        document_punishment = 1.0
        num = float(number_of_term_in_document)
        divider = term_frequence * (num * (_k + 1.0)) / (num + _k * document_punishment)
        return idf_term * divider

    def get_relvant_docs(self,parse_query, posting, num_of_docs,k=None):
        """
               This function loads the posting list and count the amount of relevant documents per term.
               :param query: query
               :return: dictionary of relevant documents.
               """
        # { doc_id: [doc tuple, list of the same terms](list in list)}
        relevant_docs = {}
        for term, freq in parse_query.items():
            # for each document we will have the word they have the
            try:  # an example of checks that you have to do
                posting_doc = posting[term][1]  # list of all doc containt term
                number_of_docs_with_term = len(posting_doc)
                for doc_tuple in posting_doc: #[()()()]
                    doc_id, doc_freq = doc_tuple
                    if doc_id not in relevant_docs.keys():
                        relevant_docs[doc_id] = 0
                    relevant_docs[doc_id] += self.weight_of_term(freq, num_of_docs, number_of_docs_with_term, freq)
            except:
                print()
        return self.rank_relevant_docs(relevant_docs,k)