import traceback

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.tag.simplify import simplify_wsj_tag DEPRECATED! NLTK 2.0 version
from nltk.tag import pos_tag, map_tag


from TweetUtils.helpers.globals import g


class POSTagger(object):
    """
    Handles postagging, stemming, lemmatizing.
    """
    def __init__(self):
        ########### POS Tagging ############
        self.bigram_tagger = []
        self.words_pos_tags2 = []
        self.words_pos_tags = {}
        self.simplified = []
        ############ N-grams ###############
        self.trigram_tagger = []
        self.gate_tagger = []
        ############ Stemming ###############
        self.init_stemmers()
        ############# Lemmatizing ###########
        self.lemmatizer = WordNetLemmatizer()

    def pos_stem_lematize(self, tweet):
        self.tweet = tweet
        self.tweet_words_in_a_single_list = self.get_tweet_words_in_a_single_list()
        self.gate_experimental_pos_tagging_using_model()
        self.bigram_pos_tagger()

        return self.tweet.pos_tagged_text

    def pos_tag_words(self):
        """
        Get pos tag for every valid word in each sentence.
        Updates self.words_pos_tags with pos tagged sentences. Result will be like: [[pos tagged sentence 1],[...2]]
        :return:None
        """
        try:
            #fixed bug 2-2-2013
            self.words_pos_tags.update(pos_tag(self.tweet_words_in_a_single_list))  #todo what about when we have more than 1 sentence? to be checked
            self.words_pos_tags2 = pos_tag(self.tweet_words_in_a_single_list)
            self.simplified = [(word, pos_tag(tag)) for word, tag in self.words_pos_tags2]
            g.logger.info("pos_tag_words:::\t"+str(self.words_pos_tags)+'\t'+str(self.words_pos_tags2))
            g.logger.info("pos_tag_words simplified:::\t"+str(self.simplified))
        except:
            g.logger.error(("could not pos tag:" + str(self.tweet.words)))

    def trigram_pos_tag_words(self):
        """
            Use a trigram tagger to get better results for aspect analysis.
        """
        tagged_corpora = []
        tweet_words = self.tweet_words_in_a_single_list
        tagged_corpora.append(pos_tag(tweet_words))                         # tagged sentences with pos_tag

        if len(tagged_corpora) > 0:
            try:
                g.logger.info(str(tagged_corpora))
                trigram_tagger = nltk.TrigramTagger(tagged_corpora)         # build trigram tagger based on your tagged_corpora
                trigram_tag_results = trigram_tagger.tag(tweet_words)       # tagged sentences with trigram tagger
                for j in range(0, len(tagged_corpora)):
                    if tagged_corpora[j][1] == 'NN':
                        tagged_corpora[j][1] = trigram_tag_results[j][1]    # for 'NN' take trigram_tagger instead

                self.trigram_tagger = tagged_corpora
                g.logger.info("trigrams:::\t" + str(tagged_corpora))
                g.logger.info("trigram results:::\t" + str(trigram_tag_results))
            except:
                g.logger.error("problem in trigram.")
                traceback.print_exc()

    def bigram_pos_tagger(self):
        self.bigram_tagger = nltk.bigrams(self.tweet.pos_tagged_text)
        g.logger.info("bigrams:::"+str(self.bigram_tagger))

    def gate_experimental_pos_tagging_using_model(self):
        """
            Get pos tagging results using custom tagger with the model provided by gate twitter tagger.
            Reference: https://gate.ac.uk/wiki/twitter-postagger.html
            L. Derczynski, A. Ritter, S. Clarke, and K. Bontcheva, 2013: "Twitter
            Part-of-Speech Tagging for All: Overcoming Sparse and Noisy Data". In:
            Proceedings of the International Conference on Recent Advances in Natural
            Language Processing.
        """
        default_tagger = nltk.data.load(nltk.tag._POS_TAGGER)
        train_model = g.train_model
        tagger = nltk.tag.UnigramTagger(model=train_model, backoff=default_tagger)
        self.gate_tagger = tagger.tag(self.tweet_words_in_a_single_list)
        g.logger.info('gate_tagger :::\t'+str(self.gate_tagger))
        self.tweet.pos_tagged_text = dict(self.gate_tagger)
        g.logger.debug('self.tweet.pos_tagged_words = self.gate_tagger: %s'%self.tweet.pos_tagged_text)

    # ================================================= STEMMING  ==================================================== #
    def init_stemmers(self):
        self.porter_stemmer = nltk.PorterStemmer()
        self.lancaster_stemmer = nltk.LancasterStemmer()
        self.regex_stemmer = nltk.RegexpStemmer('^\w')
        self.iris_stemmer = nltk.ISRIStemmer()
        self.rspl_stemmer = nltk.RSLPStemmer()

    # =================================================  HELPERS  ==================================================== #
    def get_tweet_words_in_a_single_list(self):
        tweet_words = []
        try:
            if type(self.tweet.words[0]) == list:
                for each in self.tweet.words:
                    tweet_words += each
            else:
                tweet_words = self.tweet.words
        except IndexError:
            tweet_words = self.tweet.words

        for each in tweet_words:
            tweet_words[tweet_words.index(each)] = each.encode('utf-8')

        return tweet_words
