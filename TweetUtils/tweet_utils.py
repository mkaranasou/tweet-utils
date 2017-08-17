# import copy
# import traceback
from threading import Thread
import datetime
from TweetUtils.cleaning.text_cleaner import TextCleaner
from TweetUtils.feature_extraction.text_tagger import TextTagger
from TweetUtils.helpers.exceptions import InvalidConfiguration
from TweetUtils.models.config import Config
from TweetUtils.models.tweet import Tweet
import concurrent.futures
# from TweetUtils.models.Options import FeatureOption
# from multiprocessing import Pool
# from time import sleep
# from TweetUtils.helpers.globals import g


class TweetUtils(object):
    """
    TweetUtils performs text cleaning and feature extraction of tweets according to the given configuration.
    """
    def __init__(self, configuration):
        if configuration is None:
            raise InvalidConfiguration("No configuration provided!")
        if type(configuration) is not Config:
            raise InvalidConfiguration("Wrong type of Configuration provided!")
        self.configuration = configuration
        self.tweet_list = None
        self.tweet_text = None
        self.results = None
        self.text_tagger = None
        self.text_cleaner = None
        self.input_file_path = None
        self.output_file_path = None
        self.delimiter = None
        self.include_original = True
        self.THREAD_LIST = []

    def process(self, tweet_list_or_text,
                input_file_path=None,
                output_file_path=None,
                delimiter=";",
                include_original=True):
        """
        Returns a list of processed Tweet objects.
        In case input_file_path and output_file_path are specified, tweet_list_or_text is ignored and the result is
        stored in output_file_path file in the form of:
        tweet text {delimiter} cleaned tweet text {delimiter} feature dictionary
        :param tweet_list_or_text: a list of tweet text of a single tweet text
        :param input_file_path: optional: file to read tweet text from - one per line
        :param output_file_path: optional: file to store processed tweet text
        :param delimiter: optional: default is comma ; . It is used when input_file_path and output_file_path are set
        :param include_original: boolean to indicate if the original tweet text will be included in the output_file_path
        :return: results: list of Tweet objects
        """
        self.results = []
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.delimiter = delimiter
        self.include_original = include_original

        if self.input_file_path is not None and self.output_file_path is not None:
            import os
            if not os.path.isfile(self.input_file_path):
                raise IOError("Input file path is not correct!")
            # if not os.path.isfile(self.output_file_path):
            #     raise IOError("Output file path is not correct!")
            self._read_input_file_contents()
            self._write_results_to_file()

        else:
            if type(tweet_list_or_text) is list:
                self.tweet_list = tweet_list_or_text
                i = 0
                for tweet_text in self.tweet_list:
                    self.results.append(self._process(tweet_text))
                    i += 1
                    if i % 10 == 0:
                        print i, datetime.datetime.now()
            elif type(tweet_list_or_text) is str:
                self.results = self._process(tweet_list_or_text)

            else:
                raise InvalidConfiguration("Wrong parameter types for function")
        return self.results

    def _read_input_file_contents(self):
        with open(self.input_file_path, 'rb') as in_file:
            all_lines = in_file.readlines()
            executor = concurrent.futures.ProcessPoolExecutor(self.configuration.num_of_threads)
            futures = [executor.submit(self.test, item) for item in all_lines]
            concurrent.futures.wait(futures)

            for line in in_file.readlines():
                self.results.append(self._process(line.strip('\n').strip('\r')))

    def _write_results_to_file(self):
        with open(self.output_file_path, 'a') as out_file:
            for each in self.results:
                if self.include_original:
                    out_file.write(each.text.strip("\n").strip("\r")
                                   + self.delimiter
                                   + " ".join(each.words)
                                   + self.delimiter
                                   + str(each.feature_dict) + "\n")
                else:
                    out_file.write(str(each.feature_dict) + "\n")

    def test(self, line):
        self.results.append(self._process(line.strip('\n').strip('\r')))
        with open(self.output_file_path, 'a') as out_file:
                for each in self.results:
                    if self.include_original:
                        out_file.write(each.text.strip("\n").strip("\r")
                                       + self.delimiter
                                       + " ".join(each.words)
                                       + self.delimiter
                                       + str(each.feature_dict) + "\n")
                    else:
                        out_file.write(str(each.feature_dict) + "\n")

    def _process(self, tweet_text):
        """
            Creates a tweet object using tweet_text and processes it depending on configuration.
            :param tweet_text:
            :type tweet_text: str
            :return: Tweet object processed
            :rtype: Tweet
        """
        self._init_processors()

        if type(tweet_text) is str:
            tweet = Tweet(None, tweet_text, self.text_tagger, self.text_cleaner)
            # # First process morphological features
            if self.configuration.feature_options is not None:
                tweet.tag()
            # Then proceed to cleaning
            if self.configuration.cleaning_options is not None:
                tweet.clean()
                tweet.spell_check()
                if self.configuration.feature_options is not None:
                    # postags must be the first to be processed because the following features require pos-tagged text
                    if self.configuration.feature_options.get_feature_by_name("__postags__") is not None:
                        tweet.pos_tag()

                    # calculate sentiwordnet score for each word
                    if self.configuration.feature_options.get_feature_by_name("__s_word__") is not None:
                        tweet.get_swn_score()

                    # calculate sentiwordnet score for the whole tweet
                    if self.configuration.feature_options.get_feature_by_name("__swn_score__") is not None:
                        tweet.get_total_swn_score()

                    # gather all features up to now
                    tweet.gather_dicts()

                    # calculate all four types of text similarity if requested
                    if self.configuration.feature_options.get_feature_by_name("__res__") is not None:
                        tweet.feature_dict['__res__'] = tweet.get_semantic_similarity('res')
                    if self.configuration.feature_options.get_feature_by_name("__lin__") is not None:
                        tweet.feature_dict['__lin__'] = tweet.get_semantic_similarity('lin')
                    if self.configuration.feature_options.get_feature_by_name("__path__") is not None:
                        tweet.feature_dict['__path__'] = tweet.get_semantic_similarity('path')
                    if self.configuration.feature_options.get_feature_by_name("__wup__") is not None:
                        tweet.feature_dict['__wup__'] = tweet.get_semantic_similarity('wup')

                    for each in self.configuration.feature_options.extra_options:
                        if each.post_clean:
                            tweet.extra_features.append(each.function(tweet.clean_text))
                        else:
                            tweet.extra_features.append(each.function(tweet.text))

            else:
                raise Exception("Not suitable data type {0}".format(type(tweet_text)))
            return tweet

    def _init_processors(self):
        if self.configuration.feature_options is not None:
            self.text_tagger = TextTagger(self.configuration.feature_options)     # initialize Tagger w/ configuration
        if self.configuration.cleaning_options is not None:
            self.text_cleaner = TextCleaner(self.configuration.cleaning_options)  # initialize Cleaner w/ configuration

    def _init_threads(self, tweet_list_or_text, input_file_path=None, output_file_path=None, delimiter=";", include_original=True):
        for i in range(1, self.configuration.num_of_threads):
            self.THREAD_LIST.append(Thread(target=self._process, name="ThreadNo{0}".format(i),
                                    args=[]))


if __name__ == "__main__":
    # examples
    utils = TweetUtils(Config(True, True))
    # tweets = utils.process(["This is lovely!!!#NOT", "I hate Monday mornings..."])
    # for tweet in tweets:
    #     print str(tweet), tweet.feature_dict
    #
    processed_tweet = utils.process("Oh, life is not fair? I appreciate you texting me this, from your iPhone, while on vacation in Hawaii. You're so right.")
    # processed_tweet = utils.process("Oh, you don't like sarcasm? You must be so funny to hang around with.")
    print "Resnik", processed_tweet.feature_dict["__res__"]
    print "Lin", processed_tweet.feature_dict["__lin__"]
    print "Wu-Palmer", processed_tweet.feature_dict["__wup__"]
    print "Path", processed_tweet.feature_dict["__path__"]
    print str(processed_tweet.feature_dict)
    print str(processed_tweet), processed_tweet.feature_dict


def pre_clean_function(text):
    print "pre_clean_function", text
    return "new pre-clean feature added"


def post_clean_function(text):
    print "post_clean_function", text
    return "new post-clean feature added"


# if __name__ == "__main__":
#
#     # examples
#     utils_cfg = Config(True, True)
#     utils_cfg.feature_options.add_feature(FeatureOption("test", function=pre_clean_function))
#     utils_cfg.feature_options.add_feature(FeatureOption("test", post_clean=True, function=post_clean_function))
#     utils = TweetUtils(utils_cfg)
#     tweet = utils.process(["This is lovely!!!#NOT :( :) http://dsgrg.vom/vfda", "I hate Monday mornings... :) :( !!!"])[0]
#     print tweet.clean_text
#     print tweet.feature_dict
#     print tweet.extra_features[0]
#     print tweet.extra_features[1]
#     # completed = 0
#     # q ="SELECT id, text FROM SentiFeed.TweetFinalTestData;"
#     # q_update = """UPDATE `SentiFeed`.`TweetFinalTestData`
#     #             SET `feature_dict` = "{0}"
#     #             WHERE `id` = {1};
#     #           """
#     #
#     # data = g.mysql_conn.execute_query(q)
#     # def process(tweet_tuple):
#     #     global completed
#     #     try:
#     #         utils = TweetUtils(Config(True, True))
#     #         txt = tweet_tuple[1].replace("\n", "").replace("'", "\'").replace("\"", "\\\"").replace("\r", "")
#     #         tweet = utils.process(txt)
#     #         q_res = q_update.format(str(tweet.feature_dict), tweet_tuple[0])
#     #         g.mysql_conn.update(q_res)
#     #     except:
#     #         traceback.print_exc()
#     #         print tweet_tuple
#     #         g.logger.error(tweet_tuple)
#     #     completed += 1
#     #     if completed % 100 == 0:
#     #         print completed, datetime.datetime.now()
#     #
#     # print "start", datetime.datetime.now()
#     #
#     # num_of_threads = 1
#     # skip = 0
#     # len_all = len(data)
#     # print len_all
#     # pool = Pool(processes=num_of_threads)
#     # pool.map(process, data)
#     # print completed
#     # print "finished", datetime.datetime.now()
