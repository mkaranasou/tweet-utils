# coding: utf-8

import re
import string
import traceback
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import sent_tokenize
from TweetUtils.helpers.globals import g


__author__ = 'maria'


class TextCleaner(object):
    """
    Responsible for the cleaning of a Tweet
    config: Config instance that holds neccessary information for the cleaning process
    """
    def __init__(self, config, tag=False):
        self.config = config
        self.stop_words_additional = self.config.additional_stop_words
        self.tweet = ""
        self.sentence_index = 0
        self.new_hashtag_list = []
        self.final_tweet = ''
        self.uppercase_words_per_sentence = []
        self.stop_words_removed = []
        self.found_negations = False
        self.uppercase_words_per_sentence = []
        self.laughter = []
        self.negating_terms = []
        self.abbreviations = []

    def clean_tweet(self, tweet):
        """
        cleaning text process
        :return:Clean Text
        """
        self._init()
        self.tweet = tweet
        if self.config.remove_non_ascii:            # removing non-ascii characters should be mandatory
            self.remove_non_ascii_chars()

        if self.config.remove_rt:
            self.remove_rt()

        if self.config.remove_laugh:
            self.identify_and_remove_laughter()     # todo: problematic

        if self.config.split_sentences:             # should be mandatory since without this the word split must be
            self.split_sentences()                  # different

        if self.config.remove_negations:
            self.identify_negations()
        # self.has_capitals()

        if self.config.remove_urls:
            self.remove_links()

        if self.config.remove_emoticons:
            self.store_and_remove_emoticons()

        if self.config.remove_reference:
            self.remove_reference()
        # self.handle_hashtags()

        if self.config.remove_special_characters:
            self.remove_special_chars()

        if self.config.fix_space:
            self.fix_space()

        if self.config.split_words:
            self.split_words()

        self.handle_negations() # ???
        if self.config.convert_to_lower:        # should be mandatory
            self.convert_to_lower()

        if self.config.remove_multiples:
            self.remove_multiples()

        if self.config.remove_stop_words:
            self.remove_stop_words()

        self.set_final_tweet()

        return self.tweet.words

    # GENERAL HELPERS ###############################################
    def remove_non_ascii_chars(self):
        """
        to solve problem with extra / weird characters when getting data from database
        :return:
        """
        self.tweet.text = str(filter(lambda x: x in string.printable, self.tweet.text))
        self.tweet.clean_text = str(filter(lambda x: x in string.printable, self.tweet.text))

    def remove_rt(self, ):
        rt = re.findall('^.RT\s?(@\w+){0,1}:?', self.tweet.text)
        if rt is not None and len(rt) > 0:
            text = self.tweet.text
            self.tweet.processed_tagged_text = re.sub('^RT:{0,1}', "_RT_", text)
            self.tweet.clean_text = re.sub('^RT:{0,1}', '', self.tweet.clean_text)

    def identify_and_remove_laughter(self):
        # found_haha = re.findall(r"\b(((h)*(a)*)*)\b", self.tweet.text)
        # found_lol = re.findall(r"\b(l(o)*(l)*)\b", self.tweet.text)
        # found_rotfl = re.findall(r"\b(rotfl|rofl)\b", self.tweet.text)
        # found_omg = re.findall(r"\b((o(m)*(g)*)|o-m-g|o m g)\b", self.tweet.text)

        self.tweet.clean_text = re.sub(r"\b(((h)*(a)*)*)\b", '', self.tweet.clean_text)
        self.tweet.clean_text= re.sub(r"\b(l(o)*(l)*)\b", '', self.tweet.clean_text)
        self.tweet.clean_text= re.sub(r"\b(rotfl|rofl)\b", '', self.tweet.clean_text)
        self.tweet.clean_text = re.sub(r"\b((o(m)*(g)*)|o-m-g|o m g)\b", '', self.tweet.clean_text)

    def split_sentences(self):
        """
            Tokenize sentences with nltk -- will c if it needs changing
            :return:None
        """
        self.tweet.sentences = sent_tokenize(self.tweet.clean_text)

    def remove_links(self):
        """
            Finds http links, stores them in a list and then removes them from tweet text
            :return:
        """
        clean_list = []
        for sentence in self.tweet.sentences:
            clean_sentence = re.sub("(?P<url>https?://[^\s]+)", '', sentence)
            self.tweet.links.append(re.search("(?P<url>https?://[^\s]+)", sentence))
            clean_list.append(clean_sentence)
        self.tweet.sentences = clean_list

    def store_and_remove_emoticons(self):
        """
            Match all of the usual emoticons: :-), :), :D, :-D, :-(, :(, :)), :-((, :-)), (:
        :return:
        """
        clean_list = []
        for sentence in self.tweet.sentences:
            smiley_full_patterns = re.findall(g.SMILEY_FULL_PATTERN, unicode(sentence))
            self.tweet.smileys_per_sentence.insert(self.sentence_index, smiley_full_patterns)
            self.sentence_index += 1  # to know in which sentence the smileys belong
            clean_sentence = re.sub(g.SMILEY_FULL_PATTERN, '', sentence)
            clean_list.append(clean_sentence)
        self.tweet.sentences = clean_list

    def remove_reference(self):
        """
            Stores reference in a list and then removes it from tweet text
            :return:
        """
        clean_list = []
        for sentence in self.tweet.sentences:
            self.tweet.reference.append(re.findall('(@\w+|@\D\w+|@\w+\D)', sentence))
            self.tweet.hash_list.append(re.findall('(#\w+|#\D\w+|#\w+\D)', sentence))
            clean_sentence = re.sub('(#|@\w+|@\D\w+|@\w+\D|#\w+|#\D\w+|#\w+\D)', '', sentence)
            clean_list.append(clean_sentence)
        self.tweet.sentences = clean_list

    def remove_special_chars(self):
        """
            Will store and remove any characters like '?' '!!!' '...' to see if we can infer some meaning for sentiment
            :return:
        """
        clean_list = []
        for sentence in self.tweet.sentences:
            self.tweet.non_word_chars_removed.append(re.findall(r'\W|\d|_', sentence))
            clean_sentence = re.sub(r'\W|\d|_', ' ', sentence)
            clean_list.append(clean_sentence)
        self.tweet.sentences = clean_list

    def stopwords_removal(self, each):
        """
        Searches if a word is in stopwords list and appends it to stop words removed list
        :param clean_word_list:
        :param each:
        """
        try:
            # if word is not a negation
            if not re.findall(g.NEGATIONS_PATTERN, each):
                if any(each in c for c in self.stop_words_additional):
                    self.stop_words_removed.append(each)
                if any(each.encode() in s for s in stopwords.words()):
                    self.stop_words_removed.append(each.decode('utf-8'))
        except:
            print "problem in stop - word removal" + str(Exception)
            traceback.print_exc()

    def remove_stop_words(self):
        """
            Remove stop words - both from ntlk.stop_words and from stop_words_additional
            :return:
        """
        for word in self.tweet.words:
            if type(word) == list:
                # if we have this type : [[word1, word2..] [wordn, wordm...][] ]
                for each in word:
                    self.stopwords_removal(each)
                for item in self.stop_words_removed:
                    if item in self.tweet.words[self.tweet.words.index(word)]:
                        self.tweet.words[self.tweet.words.index(word)].remove(item)
            else:
                self.stopwords_removal(word)
                for item in self.stop_words_removed:
                    if item in self.tweet.words:
                        self.tweet.words.remove(item)

    def remove_multiples(self):
        """
        This method checks every character in a word (runs for every word in tweet) and if more than two characters in
        row are found, the rest are truncated.
        'helloooooo' will be 'helloo' and then corrected in spellchecking
        Assume that two characters in a row are valid. If not they should be corrected in spell-checking
        :return:
        """
        for word in self.get_tweet_words_in_a_single_list():
            multi_counter = 0
            index_list = []
            l_word = list(word)
            if l_word.__len__() > 2:  # It doesn' t make sense to look for multiples in words with less than 3 characters
                for i in range(0, l_word.__len__()):
                    try:
                        # if this letter equals the next letter then increment multi_counter
                        if l_word[i] == l_word[i + 1]:
                            multi_counter += 1
                        else:
                            multi_counter = 0

                    except IndexError:
                        if l_word[i] == l_word[i - 1] and l_word[i] == l_word[i - 2]:
                            multi_counter += 1
                        continue
                    try:
                        # if more than 2 duplicates, keep the index of letter to be removed
                        if multi_counter > 1:
                            g.logger.debug('multiples {0} {1}'.format(l_word[i + 1], i + 1))
                            index_list.append(i + 1)
                    except IndexError:
                        # check last letter, if it is the same as the previous and counter>1
                        if l_word[i] == l_word[i - 1] and multi_counter > 1:
                            index_list.append(i)
                        pass
                if index_list.__len__() > 0:
                    # in order to avoid index errors, start removing from the end of the word
                    reverse_indexes = sorted(index_list, reverse=True)
                    for each in reverse_indexes:
                        l_word.remove(l_word[each])

                    final_word = ''.join(l_word)
                    self.tweet.corrected_words.append([word, final_word])
                    # update initial word list with corrected word
                    try:
                        w = word
                        w[word.index(word)] = final_word
                        self.tweet.words[self.tweet.words.index(word)] = w
                    except TypeError:
                        w = final_word
                        self.tweet.words[self.tweet.words.index(word)] = w

    def split_words(self):
        """
            Split each sentence into words
            :return:
            """
        for sentence in self.tweet.sentences:
            try:
                self.tweet.words.append(word_tokenize(sentence.encode('utf-8')))
            except:
                self.tweet.words.append(word_tokenize(sentence))

    def fix_space(self):
        """
            reduces multiple whitespace characters into a single space.
            :return:
        """
        clean_list = []
        for sentence in self.tweet.sentences:
            clean_sentence = ' '.join(sentence.split())
            clean_list.append(clean_sentence)
        self.tweet.sentences = clean_list

    def convert_to_lower(self):
        """convert every word to lowercase to have better results in matching
            :return:None
        """
        temp_wordlist = []
        for i in self.tweet.words:
            for word in i:
                temp_wordlist.append(word.lower())
        self.tweet.words = temp_wordlist

    def handle_hashtags(self):
        """
            Tto try get the aspect out of hashtags -- just to have some comparison for pos tag aspect
            assumption is that hashtag will be splittable by capitals //Pascal or camelCase like
            :return:None
        """
        for hashtag in self.tweet.hash_list:
            self.new_hashtag_list.append([a for a in re.split(r'([A-Z][a-z]*\d*)', str(hashtag)) if a])

    def set_final_tweet(self):
        self.final_tweet = " ".join(self.tweet.words)
        self.tweet.processed_tweet = self.final_tweet

    def identify_negations(self):
        """
            Preliminary negation check. If negations are found, we set flag to True, so that we know we should check
            afterwards
            :return:
            """
        find_negations = re.findall(g.NEGATIONS_PATTERN, str(self.tweet.text).lower())
        if None != find_negations and find_negations != []:
            self.found_negations = True
        #print "NEGATIONS:::", find_negations, self.found_negations

    def has_capitals(self):
        """
            keep all capitalized words along with the sentence index they belong
            :return:None
            """
        for s in self.tweet.sentences:
            if self.tweet.sentences.__len__() > 1:
                for word in s.split(' '):
                    if word.isupper():
                        self.tweet.uppercase_words_per_sentence.append([self.tweet.sentences.index(s), word])
            else:  # todo: rethink about it...
                if s.isupper():
                    self.tweet.uppercase_words_per_sentence.append([self.tweet.sentences.index(s), s])

    def has_negations(self, word):
        """

            :param word:
            :return: :rtype:
        """
        return re.findall(g.NEGATIONS_PATTERN, word.lower())

    def keep_negated_term(self, each, word):
        try:
            self.negating_terms.append(word[word.index(each) + 1])
        except IndexError:
            try:
                if word.__len__() > 1:
                    self.negating_terms.append(word[word.index(each) - 1])
                else:
                    g.logger.debug("In keep negating term::: word len == {0}".format(word.__len__()))
            except AttributeError:
                pass

    def handle_negations(self):
        """ keep position of negation in sentence and negation
                final list should look like: [[1, 'no'],[4, 'not']] etc
        """
        if self.found_negations:
            for word in self.tweet.words:
                if type(word) == list:
                    for each in word:
                        exists = self.has_negations(each)
                        if exists != [] and None != exists:
                            self.tweet.negations.append((each, word.index(each)))
                            self.keep_negated_term(each, word)
                else:
                    for word in self.tweet.words[0]:
                        exists = self.has_negations(word)
                        if exists != [] and None != exists:
                            self.tweet.negations.append((word, self.tweet.words[0].index(word)))
                            self.keep_negated_term(word, self.tweet.words[0])
            if self.tweet.negations.__len__() > 0:
                pass
            else:
                pass

    def get_tweet_words_in_a_single_list(self):
        """
            To overcome the problem of self.tweet.words = [[''],[''],...] or ['','','']
            :return: returns a single list of words
            :rtype:list
        """
        tweet_words = []
        try:
            if type(self.tweet.words[0]) == list:
                for each in self.tweet.words:
                    tweet_words += each
            else:
                tweet_words = self.tweet.words
            return tweet_words
        except IndexError:
            return tweet_words

    def _init(self):
        self.tweet = ""
        self.sentence_index = 0
        self.new_hashtag_list = []
        self.final_tweet = ''
        self.uppercase_words_per_sentence = []
        self.stop_words_removed = []
        self.found_negations = False
        self.uppercase_words_per_sentence = []
        self.laughter = []
        self.negating_terms = []
        self.abbreviations = []