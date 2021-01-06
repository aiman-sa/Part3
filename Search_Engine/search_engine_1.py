import time
import pandas as pd
from parser_module import Parse
from indexer import Indexer
import numpy as np
from searcher import Searcher
from scipy import linalg

class SearchEngine:

    def __init__(self,config=None):
        self.Config = config
        self._indexer = Indexer(config)
        self._parser = Parse(self._indexer,False)
        self._model = None
        self._matrix={}
        #self._matrix[0] = self._indexer.postingDict.keys()
        #self._dataFrame={}

    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        start_time = time.time()
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
            self._matrix[parsed_document.tweet_id]=parsed_document.term_doc_dictionary
        print('Finished parsing and indexing.')
        self._indexer.save_index("posting")
        print(time.time() - start_time)


    def load_precomputed_model(self,model_dir):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        self._model=self

    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """

        searcher = Searcher(self._parser, self._indexer, model=self._model)
        self.createMatrix(query)
        searcher.DT=self.DT
        searcher.q=self.q
        return searcher.search(query)

    def createMatrix(self,query):
        d = {}
        dictFromQuery = {}
        self._parser.tokenSplit(query, dictFromQuery)
        col = len(dictFromQuery)
        vectorQuery = np.ones((col,), dtype=int)
        for term in dictFromQuery.keys():
            lst=self.getListTerms(term) #[1,[]]
            for tuple1 in lst[1]:
                d[tuple1[0]]=pd.Series(self.getFreq(dictFromQuery,tuple1[0]),index=[*dictFromQuery])

        dataFrame=pd.DataFrame(d)
        T, S, self.DT = linalg.svd(dataFrame, full_matrices=False)
        InvS=np.zeros((len(S), len(S)))
        for i in range(len(S)):
            if S[i]==0:
                InvS[i][i] = 0
            else:
                InvS[i][i]=1/S[i]
        #InvS = np.linalg.inv(matrixS)
        #transDt=np.transpose(self.DT)
        vectorQueryTrans = np.transpose(vectorQuery)
        temp = np.dot(vectorQueryTrans,T)
        self.q = np.dot(temp, InvS)

    def getFreq(self,dictQuery,tweetId):
        lst=[]
        for term in dictQuery.keys():
            if term.lower() in self._matrix[tweetId]:
                lst.append(self._matrix[tweetId][term.lower()])
            elif term.upper() in self._matrix[tweetId]:
                lst.append(self._matrix[tweetId][term.upper()])
            else:
                lst.append(0)
        return lst
    def getListTerms(self,term):
        if term.lower() in self._indexer.postingDict:
            return self._indexer.postingDict[term.lower()]
        elif term.upper() in self._indexer.postingDict:
            return self._indexer.postingDict[term.upper()]
    def getIndex(self,term):
        if term.lower() in self._indexer.postingDict:
            return list(self._indexer.postingDict.keys()).index(term.lower())
        elif term.upper() in self._indexer.postingDict:
            return list(self._indexer.postingDict.keys()).index(term.upper())

