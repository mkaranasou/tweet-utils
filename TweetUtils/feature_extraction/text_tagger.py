__author__ = 'maria'

import re
import traceback
from hashtag_handler import HashTagHandler

__author__ = 'maria'
from TweetUtils.helpers.globals import g


class TextTagger(object):
    """
    TextTagger is responsible for applying identified tags to a cleaned text.
    The result text should be:
    {REFERENCE} {LINK}
    and the result dictionary:
    _tags = {
    ...
    "CAPITAL" : "True",
    ...
    }

    """

    _initial_values = [False, "False", "", 0]

    def __init__(self, feature_configuration):
        self.initial_text = ""
        self.tagged_text = ""
        self.tag_pattern = " {%s} "
        self.ht_handler = HashTagHandler()
        self.feature_configuration = feature_configuration
        self._tags = None
        self._patterns = None
        self._init_configuration()

    def tag_text(self, text):
        """
        replaces text_to_tag tag part with appropriate tag label
        e.g. http://... ==> {LINK}
        """
        self.ht_handler.reset()
        self.initial_text = text
        self.tagged_text = text
        self.reset()
        for key in self._patterns:

            if key == g.TAGS.__CAPITAL__:
                match = re.findall(self._patterns[key], self.initial_text)
                if match.__len__() > 0:
                    self.tagged_text += self.tag_pattern % self._tag(key)
                    self._tags[g.TAGS.name[key]] = "True"

            elif key == g.TAGS.__HT__:
                # find all hashtags
                ht = re.findall(self._patterns[key], self.initial_text)

                if None != ht and [] != ht:                         # if found
                    ht_key = ''
                    if type(ht) == list:                            # if more than one
                        for each in ht:                             # for each in found hashtags
                            ht_key = self.ht_handler.handle(each)   # find if it is a positive or negative or neutral
                    else:                                           # not a list
                        ht_key = self.ht_handler.handle(ht)         # find if it is a positive or negative or neutral
                    self.tagged_text = re.sub(self._patterns[key], self.tag_pattern % self._tag(key), self.tagged_text.lower())
                    self._tags[g.TAGS.name[ht_key]] = "True"   # replace the final verdict
                                                                          # of Hashtag handler with "True"
            elif key == g.TAGS.__HT_NEG__ or key == g.TAGS.__HT_POS__:
                pass
            else:
                if re.findall(self._patterns[key], self.initial_text):
                    self._tags[g.TAGS.name[key]] = "True"
                    self.tagged_text = re.sub(self._patterns[key], self.tag_pattern % self._tag(key), self.tagged_text.lower())
                    if key == g.TAGS.__LINK__:
                        self.initial_text = re.sub(self._patterns[key], "", self.initial_text)
                if re.findall(self._patterns[key], self.initial_text.lower()):
                    self._tags[g.TAGS.name[key]] = "True"
                    self.tagged_text = re.sub(self._patterns[key], self.tag_pattern % self._tag(key), self.tagged_text.lower())
                    if key == g.TAGS.__LINK__:
                        self.initial_text = re.sub(self._patterns[key], "", self.initial_text)
        return self.tagged_text

    def _tag(self, tag):
        return g.TAGS.name[tag]

    def reset(self):
        for key in self._tags.keys():
            self._tags[key] = "False"

    def _init_configuration(self):
        self._tags = self.feature_configuration.get_tags()
        self._patterns = self.feature_configuration.get_patterns()
        # for feature_name, value in self._tags.items():
        #     exists = [a for a in self.feature_configuration if a.name == feature_name]
        #     if len(exists) == 0:
        #         del self._tags[feature_name]
        #
        #     else:
        #         self._patterns[feature_name] = exists[0].regex
        #         self._tags[feature_name] = self._init_data_type(exists[0])

    def _init_data_type(self, feature):
        if feature.value in range(0, len(self._initial_values)):
            return self._initial_values[feature.value]

        else:
            raise Exception("No suitable type of feature: {0}".format(feature.value))

