from TweetUtils.helpers.globals import g
__author__ = 'm.karanasou'


class PriorPolarity(object):
    """
    Given a tweet, calculate the SentiWordNet score for each word and store it in
    self.tweet.swn_score_dict['__s_word-1'] = 1.5
    While calculating
    """
    def __init__(self, tweet):
        self.tweet = tweet

    def get_simple_pos_for_swn(self, word):
        if self.tweet.pos_tagged_text[word] in g.NOUNS:
            return ' and Category = "n" '
        elif self.tweet.pos_tagged_text[word] in g.VERBS:
            return ' and Category = "v" '
        elif self.tweet.pos_tagged_text[word] in g.ADVERBS:
            return ' and Category = "r" '
        elif self.tweet.pos_tagged_text[word] in g.ADJECTIVES:
            return ' and Category = "a" '
        return ""

    def get_total(self):

        excluded = [a for a in self.tweet.words if len(a) < 2]
        num_excluded = len(excluded)
        num_total_words = len(self.tweet.words)
        final = sum(self.tweet.swn_score_dict.values())

        if num_total_words > num_excluded and num_total_words > 0:
            self.tweet.swn_score = round(final/float(num_total_words - num_excluded), 2)
        else:
            if num_total_words > 0:
                self.tweet.swn_score = round(final/float(num_total_words), 2)
            else:
                self.tweet.swn_score = 1.0  # neutral

        if self.tweet.tags[g.TAGS.name[g.TAGS.__NEGATION__]] or\
           self.tweet.tags[g.TAGS.name[g.TAGS.__AS_GROUND_AS_VEHICLE__]]:
            if self.tweet.swn_score >= 1:
                self.tweet.swn_score -= 0.5
            else:
                self.tweet.swn_score *= 0.5

    def get_polarity(self, method='sum'):

        calculate_fn = self._calculate_sum_score if method == 'sum' \
                        else self._calculate_ranking_score

        for word in self.tweet.words:
            calculate_fn(word)

    def _calculate_sum_score(self, word):
        """
        Get score - simple sum
        :param word:
        :return:
        """

        word = word.encode('utf-8')
        if len(word) > 1:
            try:
                # first try get equals score with category
                score = g.mysql_conn.execute_query(g.sum_query_figurative_scale_equals()
                                                    .format(word, self.get_simple_pos_for_swn(word)))
            except:
                g.logger.error(g.sum_query_figurative_scale_equals().format(word, self.get_simple_pos_for_swn(word)))
                # if that failed, try get equals without category
                score = g.mysql_conn.execute_query(g.sum_query_figurative_scale_equals().format(word, ""))
                g.logger.debug("tried equals for {0} and got {1}".format(word, score[0][0]))

            if score[0][0] > 2.0:
                # if that failed, try get like with category
                stemmed_word = self.tweet.pos_tagger.lancaster_stemmer.stem(word)
                try:
                    score = g.mysql_conn.execute_query(g.sum_query_figurative_scale_like()
                                                       .format(stemmed_word, self.get_simple_pos_for_swn(word)))
                    g.logger.debug("tried like for {0} and category got {1}".format(stemmed_word, score[0][0]))
                except:
                    # if that failed also, try get like without category
                    score = g.mysql_conn.execute_query(g.sum_query_figurative_scale_like()
                                                       .format(stemmed_word, ""))
                    g.logger.debug("tried like for {0} and got {1}".format(stemmed_word, score[0][0]))

            if score[0][0] is not None and score[0][0] <= 2.0:
                self.tweet.swn_score_dict['__s_word-'+str(self.tweet.words.index(word))] = round(score[0][0], 2)
            else:
                self.tweet.swn_score_dict['__s_word-'+str(self.tweet.words.index(word))] = 1

    def _calculate_ranking_score(self, word):
        pass