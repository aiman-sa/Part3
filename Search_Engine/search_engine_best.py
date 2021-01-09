from project_best.searcher import Searcher
from parser_module import Parse
from indexer import Indexer
import pandas as pd
import utils

class SearchEngine:

    def __init__(self, config=None):
        self.Config = config
        self._indexer = Indexer(config)
        self._parser = Parse(self._indexer, False)
        self._model = None
        self._doc_data_dict = {}

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
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            self.number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
            self._doc_data_dict[parsed_document.tweet_id]=parsed_document.term_doc_dictionary
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
        NUMBER_OF_LEARNING_DOC = 100
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        searcher.number_of_documents=self.number_of_documents
        dict_from_query = {}
        self._parser.tokenSplit(query, dict_from_query)
        top_doc = searcher.relevant_docs_from_posting(dict_from_query)
        top_k_docs=top_doc[:NUMBER_OF_LEARNING_DOC]
        c_matrix = self.create_c_of_doc(top_k_docs, dict_from_query)
        tempLen=len(dict_from_query)
        assoicion_matrix = self.create_association_matrix(c_matrix, dict_from_query)
        c_matrix.clear()
        self.expand_qurey(dict_from_query, assoicion_matrix)
        if len(dict_from_query)==tempLen:
            return len(top_doc),top_doc
        result=searcher.relevant_docs_from_posting(dict_from_query)
        return len(result),result


    def create_c_of_doc(self, top_relevant_docs, dict_from_query):
        c_matrix = {}
        for doc_id in top_relevant_docs:
            doc_term_freq_dict = self._doc_data_dict[doc_id] #{tweet_id:[terms:f]}
            if len(doc_term_freq_dict) == 0:
                continue
            # doc_term_freq_dict = doc_term_freq_dict[0]
            for term_doc1, term_doc_freq1 in doc_term_freq_dict.items():
                # for queryIndex in top_relevant_docs[doc_id][2]:
                if term_doc1 not in c_matrix.keys():
                    c_matrix[term_doc1] = {}
                for term_doc2, term_doc_freq2 in doc_term_freq_dict.items():
                    if term_doc1 in dict_from_query.keys() or term_doc1 == term_doc2:
                        if term_doc2 not in c_matrix[term_doc1]:
                            c_matrix[term_doc1][term_doc2] = 0
                        c_matrix[term_doc1][term_doc2] += term_doc_freq1 * term_doc_freq2  # Cii,Cjj,Cij
        return c_matrix

    def create_association_matrix(self, c_matrix, dict_from_query):
        # c_matrix will be a dic of dic  {term: totalSum}
        association_matrix = {}
        # dict build as first serch of i and then cearch j (dict inside a dict)
        for term in dict_from_query.keys():
            # get all dict of all values association with terms
            if term not in c_matrix.keys():
                continue
            association_terms_dict = c_matrix[term]
            # create a dic of all associate terms
            column_dict = {}
            association_matrix[term] = column_dict
            # run on the values and keys
            for term_key, value in association_terms_dict.items():
                c_term_key = 0
                if term_key in c_matrix.keys():
                    c_term_key = c_matrix[term_key][term_key]
                if (c_matrix[term][term] + c_term_key - value) == 0:
                    column_dict[term_key] = 0
                else:
                    column_dict[term_key] = value / (c_matrix[term][term] + c_term_key - value)
        return association_matrix

    def expand_qurey(self, dict_from_query, association_matrix):
        MIN_REQUIREDMENT = 0.8
        # the word we will insert
        insert_dic_by_term = {}  # {index: [word1,word2]}
        # run on all terms in qurey
        for term, freq in dict_from_query.items():
            # create a list to expand
            term_associated_term = []
            # save this list
            insert_dic_by_term[term] = term_associated_term
            # take the top association word with term
            if term not in association_matrix.keys():
                continue
            column = association_matrix[term]
            for inner_term, associated_value in column.items():
                #  column.item = { term : associated value}
                if associated_value >= MIN_REQUIREDMENT and inner_term != term:
                    term_associated_term.append(inner_term)
        try:
            for term, list_added_word in insert_dic_by_term.items():
                for inner_word in list_added_word:
                    dict_from_query[inner_word] = dict_from_query[term] * association_matrix[term][inner_word]
        except Exception as e:
            print(e)
        insert_dic_by_term.clear()

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self.postingDict = utils.load_obj(fn)

