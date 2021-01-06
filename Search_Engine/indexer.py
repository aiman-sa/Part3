# DO NOT MODIFY CLASS NAME
import pickle
import utils
from textblob import TextBlob


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        #self.inverted_idx = {}
        self.postingDict = {}
        self.config = config
        self.D_Count={}
        self.Entitys = {}



    def spell_correction(self,misspell_word):
        return TextBlob(misspell_word)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary  # {term:freq,term:freq}
        for term in document_dictionary:
            try:
                if term[0].isupper() and " " in term:
                    self.addEntitysToPosting(term, document.tweet_id, document_dictionary[term])
                    continue
                if term.lower() not in self.postingDict and term.upper() not in self.postingDict:
                    return
                if term.lower() in self.postingDict:
                    self.postingDict[term.lower()][1].append((document.tweet_id, document_dictionary[term]))
                elif term.upper() in self.postingDict:
                    self.postingDict[term.upper()][1].append((document.tweet_id, document_dictionary[term]))

            # max_freq = max([document_dictionary.values()])
            # self.num_in_pos_tmp += 1
            except:
                print('problem with the following key {}'.format(term[0]))
        # max_freq = max([document_dictionary.values()])
        # self.tmp_pos[('Document', document.tweet_id)] = document_dictionary
        # self.D_Count[document.tweet_id]=sum(document_dictionary.values())

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        print('Load inverted index')
        inverted_index = utils.load_obj(fn)
        return inverted_index


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        with open(fn, 'wb') as f:
            pickle.dump(self.postingDict, f, pickle.HIGHEST_PROTOCOL)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def addEntitysToPosting(self, term, tweet_id, quantity):
        if term not in self.postingDict:
            return
        if term.upper() not in self.Entitys and term.upper() not in self.postingDict:  # Entitys=>{"DONALD TRUMP:(12,3)},inverted_idx=> {DONALD TRUMP}
            self.Entitys[term.upper()] = (tweet_id, quantity)
        else:
            if term.upper() not in self.postingDict:
                self.postingDict[term.upper()] = [1, []]
                self.postingDict[term.upper()][1].append(self.Entitys[term.upper()])
            self.postingDict[term.upper()][1].append((tweet_id, quantity))
            self.postingDict[term.upper()][0] += 1
            if term.upper() not in self.postingDict:
                self.postingDict[term.upper()] = []
            self.postingDict[term.upper()].append((tweet_id, quantity))




