import pandas as pd
from parser_module import Parse
from indexer import Indexer
from project_3.searcher import Searcher
from project_3.indexer import Indexer

class SearchEngine:

    def __init__(self,config=None):
        self.Config = config
        self._indexer = Indexer(config)
        self._parser = Parse(self._indexer, False)
        self._model = None
        self._dataFrame = {}

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
        self.number_of_documents = 0
        # documents_list = r.read_file(i)
        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            self.number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        print('Finished parsing and indexing.')


    def load_precomputed_model(self,model_dir):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

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
        searcher.number_of_documents=self.number_of_documents
        return searcher.search(query)