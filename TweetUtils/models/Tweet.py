import re
from nltk.corpus import wordnet
from TweetUtils.feature_extraction.PriorPolarity import PriorPolarity
from TweetUtils.helpers.pyenchant_spell_checker import EnchantSpellChecker
from TweetUtils.feature_extraction.POSTagger import POSTagger
from TweetUtils.feature_extraction.SemanticAnalyser import SemanticAnalyzer
from TweetUtils.helpers.globals import g


__author__ = 'maria'


class Tweet(object):
    """

    """
    def __init__(self, id_, text, text_tagger, text_cleaner, train=0, clean_text=None):
        self.id = id_
        self.text = text
        self.clean_text = clean_text if clean_text is not None else ""
        self.tagged_text = None
        self.pos_tagged_text = {}
        self.tags = {}
        self.initial_score = 0.0
        self.spellchecker = EnchantSpellChecker()
        self.spellchecker.dict_exists('en')
        self.sentences = []
        self.words = []
        self.links = []
        self.corrected_words = []
        self.smileys_per_sentence = []
        self.uppercase_words_per_sentence = []
        self.reference = []
        self.hash_list = []
        self.non_word_chars_removed = []
        self.negations = []
        self.swn_score_dict = {}
        self.swn_score = 1.0
        self.similarity = 0.0
        self.feature_dict = {}
        self.words_dict = {}
        self.words_to_swn_score_dict = {}
        self.train = train
        self.extra_features = []
        # ========== Helpers ============ #
        self.tagger = text_tagger
        self.text_cleaner = text_cleaner
        self.pos_tagger = POSTagger()
        self.semantic_analyser = SemanticAnalyzer()
        self.prior_polarity_calc = None
        # self.prior_polarity = PriorPolarity()

    def __str__(self):
        return self.text

    def tag(self):
        self.tagged_text = self.tagger.tag_text(self.text)
        self.tags = self.tagger._tags

    def clean(self):
        clean_words = self.text_cleaner.clean_tweet(self)
        self.clean_text = ' '.join(clean_words)

    def spell_check(self):
        for word in self.words:
            if self.contains_errors(word):
                corrected = self.spellchecker.correct_word(word)
                self.words[self.words.index(word)] = corrected[0].replace("'", " ").replace("\"", " ") if len(corrected) > 0 else word

    def pos_tag(self):
        self.pos_tagged_text = self.pos_tagger.pos_stem_lematize(self)
        g.logger.debug("POS-TAGS: %s" % self.pos_tagged_text)

    def get_simple_pos_for_swn(self, word):
        if self.pos_tagged_text[word] in g.NOUNS:
            return ' and Category = "n" '
        elif self.pos_tagged_text[word] in g.VERBS:
            return ' and Category = "v" '
        elif self.pos_tagged_text[word] in g.ADVERBS:
            return ' and Category = "r" '
        elif self.pos_tagged_text[word] in g.ADJECTIVES:
            return ' and Category = "a" '
        return ""

    def fix_words(self):
        for word in self.words:
            self.words[self.words.index(word)] = self.pos_tagger.lancaster_stemmer.stem(word)

    def fix_pos_tagging(self):
        for each in self.pos_tagged_text.keys():
            temp = self.pos_tagged_text[each]
            stemmed = self.pos_tagger.lancaster_stemmer.stem(each)
            del self.pos_tagged_text[each]
            self.pos_tagged_text[stemmed] = temp

    def get_swn_score(self):
        """
        Calculate SentiWordNet score for each word
        """
        self.prior_polarity_calc = PriorPolarity(self)
        self.prior_polarity_calc.get_polarity('sum')

    def get_total_swn_score(self):
        """
        Calculate average SentiWordNet score
        :return: None
        """
        self.prior_polarity_calc.get_total()

    def get_semantic_similarity(self, type_):
        similarity = 0.0
        nouns = []
        verbs = []
        adj = []
        adv = []
        for each in self.pos_tagged_text.items():
            if each[1] in g.NOUNS:
                nouns.append((each[0], wordnet.NOUN))
            elif each[1] in g.VERBS:
                verbs.append((each[0], wordnet.VERB))
            elif each[1] in g.ADJECTIVES:
                adj.append((each[0], wordnet.ADJ))
            elif each[1] in g.ADVERBS:
                adv.append((each[0], wordnet.ADV))

        final_list = [nouns, verbs, adj, adv]
        final_list_names = ["nouns", "verbs", "adj", "adv"]
        length = 0.0
        for each in final_list:
            if len(each) > 1:
                for i in range(1, len(each)):
                    temp_similarity = self.semantic_analyser.get_similarity(each[i-1][0],
                                                                     each[i][0],
                                                                     each[i][1],
                                                                     type_)
                    if temp_similarity is not None:
                        similarity += temp_similarity
                        length += 1.0

        if length > 0:
            g.logger.debug("length %s" % length)
            self.similarity = float(similarity/length)
        else:
            g.logger.debug("length 0 similarity %s" % similarity)
            self.similarity = 1.0
        return self.similarity

    def get_words_to_swn_score_dict(self):
        for word in self.words:
            lemmatized_word = self.pos_tagger.lemmatizer.lemmatize(word, self.pos_tagged_text[word])
            self.words_to_swn_score_dict[lemmatized_word] = self.swn_score_dict['__s_word-'+str(self.words.index(word))]

    def get_words_dict(self):
        for word in self.words:
            self.words_dict['word-'+str(self.words.index(word))] = word
        return self.words_dict

    def gather_dicts(self):
        self.feature_dict = dict(self.swn_score_dict.items() +
                                 self.tags.items() +
                                 self.pos_tagged_text.items() +
                                 self.get_words_dict().items() +
                                 self.words_to_swn_score_dict.items())

        self.feature_dict["__swn_score__"] = self.swn_score

    def contains_errors(self, word):
        return self.spellchecker.spell_checker_for_word(word) is not None
