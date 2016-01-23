import nltk

__author__ = 'maria'

import re
from TweetUtils.helpers.globals import g
import TweetUtils.helpers.pyenchant_spell_checker as sp_ch


class HashTagHandler(object):
    """
    The idea is to:
    1. First check if whole hashtag consists of CAPITALS
        if yes: then have a check to tell if it is spelled correctly
        else: goto 3.
    2. Try split hashtag by Capitals, e.g.: #ThisIsAHashtag ==> This Is A Hasthag
        - have a check to tell if every word is spelled correctly
        else: goto 3.
    3. Spellcheck those who are not
    """

    def __init__(self):
        self.hashtag = None
        self.spell_checker = sp_ch.EnchantSpellChecker()
        self.spell_checker.dict_exists('en')
        self.handled_hashtag = []
        self.lancaster_stemmer = nltk.LancasterStemmer()

    def _set_hasthag(self, hashtag):
        self.hashtag = hashtag
        self.handled_hashtag = []

    def handle(self, hashtag):
        self._set_hasthag(hashtag.replace("#", ""))
        if self._is_every_letter_capital():                                             # CAPITALS
            if self._is_spelling_correct(self.hashtag):                                 # CORRECT CAPITALS
                self.handled_hashtag.append(self._get_score_for_hasthag(self.hashtag))  # GET SCORE
            else:                                                                       # NOT CORRECT CAPITALS
                self.hashtag = self._try_spellcheck(self.hashtag)                       # TRY SPELL CHECK
                if self._is_spelling_correct(self.hashtag):                             # CHECK CORRECT CAPITALS AGAIN
                    self.handled_hashtag.append(self._get_score_for_hasthag(self.hashtag))  # IF GOOD GET SCORE
                else:
                    self.handled_hashtag.append(g.TAGS.__HT__)                              # ELSE JUST RETURN HT TAG
        else:
            words = self._try_split_hashtag_by_capitals(self.hashtag.replace("#", ""))  # NOT ALL LETTERS CAPITAL
            for word in words:
                if self._is_spelling_correct(word):                                     # IF SPLIT WORD IS CORRECT
                    self.handled_hashtag.append(self._get_score_for_hasthag(word))      # TRY GET SCORE
                else:
                    self._try_spellcheck(word)                                          # ELSE TRY SPELLCHECK
                    if self._is_spelling_correct(word):                                 # CHECK AGAIN
                        self.handled_hashtag.append(self._get_score_for_hasthag(word))
                    else:
                        self.handled_hashtag.append(g.TAGS.__HT__)

        return self._calculate_result()

    def _is_every_letter_capital(self):
        all_capitals = re.sub(r"[A-Z]", "", self.hashtag)
        if all_capitals.__len__() > 0:
            return False
        else:
            return True

    def _try_split_hashtag_by_capitals(self, hashtag):
        """
            To try get the aspect out of hashtags -- just to have some comparison for pos tag aspect
            assumption is that hashtag will be splittable by capitals //Pascal or camelCase like
            :return:None
        """
        split_hashtag = [a for a in re.split(r'([A-Z][a-z]*\d*)', str(hashtag)) if a]
        return split_hashtag

    def _try_spellcheck(self, word):

        suggestions = self.spell_checker.correct_word(word)

        if len(suggestions) > 0:
            word = suggestions[0]

        return word

    def _is_spelling_correct(self, word):
        if self.spell_checker.spell_checker_for_word(word) is not None:
            return False
        return True

    def _get_score_for_hasthag(self, hashtag):
        result = []
        word = hashtag.lower()
        score = g.mysql_conn.execute_query(g.sum_query_figurative_scale2_equals().format(word, ""))
        if score[0][0] > 5.0:
            g.logger.debug("greater than 5.0")
            word = self.lancaster_stemmer.stem(hashtag)
            score = g.mysql_conn.execute_query(g.sum_query_figurative_scale2_like().format(word, ""))
        if score[0][0] is not None and score[0][0] <= 5.0:
            result.append(round(score[0][0], 2))
            g.logger.debug("hastag word result : %s" % result[0])
            if result[0] > 0.0:
                return g.TAGS.__HT_POS__
            elif result[0] < 0.0:
                return g.TAGS.__HT_NEG__
            return g.TAGS.__HT__
        return g.TAGS.__HT__

    def _calculate_result(self):
        """

        :return:
        """
        g.logger.debug("handled_hashtag:%s" % self.handled_hashtag)

        if type(self.handled_hashtag) == list:
            pos = self.handled_hashtag.count(g.TAGS.__HT_POS__)
            neg = self.handled_hashtag.count(g.TAGS.__HT_NEG__)
            neu = self.handled_hashtag.count(g.TAGS.__HT__)

            if pos > neg:
                return g.TAGS.__HT_POS__
            elif (neg >= pos) and (neg >= neu) and neg > 0:
                return g.TAGS.__HT_NEG__
            else:
                return g.TAGS.__HT__
        else:
            return self.handled_hashtag

    def reset(self):
        self.hashtag = None
        self.handled_hashtag = []