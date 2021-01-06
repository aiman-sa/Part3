from nltk.stem import snowball


class Stemmer:
    def __init__(self):
        self.stemmer = snowball.SnowballStemmer("english")

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)

"""
from nltk.stem import snowball, PorterStemmer

class Stemmer:

    def __init__(self):
        self.stemmer = PorterStemmer()  # snowball.SnowballStemmer("english")

    def stem_term(self, word):
        if word[0] != '#' and word[0] != '@' and word.isalpha():
            return self.stemmer.stem(word)
        return word



"""