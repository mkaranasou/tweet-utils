import traceback
from nltk.corpus.reader import WordNetError

from nltk.corpus import wordnet as wn
from itertools import product
from TweetUtils.helpers.globals import g
from nltk.corpus import wordnet_ic

brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')

# lin and res similarity http://www.nltk.org/howto/wordnet.html

'''
http://stackoverflow.com/questions/17296588/python-nltk-returning-odd-result-for-wordnet-similarity-measure
...a score denoting how similar two word senses are,
based on the depth of the two senses in the taxonomy
and that of their Least Common Subsumer (most specific ancestor node).'''


class SemanticAnalyzer(object):
    """

    """
    def __init__(self):
        self.sum_similarity = 0.0
        self.check_count = 0

    def get_similarity(self, word1, word2, pos, type_):
        """
         Calculate the similarity metric for the two given words.
        :param word1:str, the first word
        :param word2:str, the second word
        :param pos:str, the PoS
        :param type_:str, similarity type, 'res' for Resnik, 'lin' for Lin, 'path' for Path and 'wup' for Wu-Palmer
        :return:float, the similarity result
        """
        if type_ == 'res':
            similarity = self.resnik_similarity(word1, word2)
        elif type_ == 'lin':
            similarity = self.lin_similarity(word1, word2)
        elif type_ == 'path':
            similarity = self.path_similarity(word1, word2)
        elif type_ == 'wup':
            similarity = self.wup_similarity(word1,word2)
        else:
            raise NotImplementedError

        return similarity

    def path_similarity(self, word1, word2):
        """

        :param word1:
        :param word2:
        :return:
        """
        ss1 = wn.synsets(word1)
        ss2 = wn.synsets(word2)

        try:
            return max(s1.path_similarity(s2) for (s1, s2) in product(ss1, ss2))
        except (ValueError, WordNetError):
            pass
            g.logger.error("path similarity problem:{0}".format(ss1), exc_info=True)
            return 0

    def wup_similarity(self, word1, word2):
        """

        :param word1:
        :param word2:
        :return:
        """
        ss1 = wn.synsets(word1)
        ss2 = wn.synsets(word2)
        try:
            return max(s1.wup_similarity(s2) for (s1, s2) in product(ss1, ss2))
        except (ValueError, WordNetError):
            pass
            g.logger.error("wup similarity problem:{0} {1}".format(word1, word2))

            return 0

    def resnik_similarity(self, word1, word2):
        try:
            ss1 = wn.synsets(word1)
            ss2 = wn.synsets(word2)

            return max(s1.res_similarity(s2, brown_ic) for (s1, s2) in product(ss1, ss2))
        except (ValueError, WordNetError):
            pass
            g.logger.error("resnik similarity problem:{0}".format(traceback.format_exc()))
            return 0

    def lin_similarity(self, word1, word2):
        ss1 = wn.synsets(word1)
        ss2 = wn.synsets(word2)

        try:
            return max(s1.lin_similarity(s2, brown_ic) for (s1, s2) in product(ss1, ss2))
        except (ValueError, WordNetError):
            pass
            g.logger.error("lin similarity problem:{0}".format(traceback.format_exc()))
            return 0

