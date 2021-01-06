import time

import numpy as np
from ranker import Ranker
import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.DT=None
        self.q=None


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
        relevant_docs = self._relevant_docs_from_posting(query)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        #transDt=np.transpose(self.DT)
        for i in range(self.DT.shape[1]):
            d=self.DT[:, i]
            tweetid = list(self._model._matrix)[i]
            x = np.dot(self.q, d)
            y = np.linalg.norm(self.q) * np.linalg.norm(d)
            if (y != 0 and x!=0):
                relevant_docs[tweetid] = x / y
        return relevant_docs #{12345:sim}

        #transDt=np.transpose(self.DT)
        #for i in range(len(q)):
        #    tweetid=list(self._model.columns)[i]
        #    x=np.dot(q,self.transDt[i])
        #    y=np.linalg.norm(q)*np.linalg.norm(self.transDt[i])
        #    if(y==0):
        #        relevant_docs[tweetid]=0
        #    else:
        #        relevant_docs[tweetid]=x/y
        #return relevant_docs
"""
        relevant_docs = {}
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, tf in posting_list:
                df = relevant_docs.get(doc_id, 0)
                relevant_docs[doc_id] = df + 1
        return relevant_docs
"""

# col = len(self._indexer.inverted_idx)
# vectorQuery = np.zeros((col,), dtype=int)
# for term, num in dictFromQuery.items():
#    if term.upper() in self._indexer.postingDict:
#        index = list(self._indexer.postingDict.keys()).index(term.upper())
#        vectorQuery[index] = num
#    elif term.lower() in self._indexer.postingDict:
#        index = list(self._indexer.postingDict.keys()).index(term.lower())
#        vectorQuery[index] = num
# vectorQueryTrans=vectorQuery.transpose()
# temp=np.dot(vectorQuery,self.T)
# q=np.dot(temp,self.InvS)