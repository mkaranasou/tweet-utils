from TweetUtils.helpers.globals import g, Globals

__author__ = 'maria'


class Options(object):
    def __init__(self, defaults=True):
        self.defaults = defaults

    def set_defaults(self):
        pass


class Option(object):
    """
    Represents either a cleaning or a feature option
    name: The name of the option
    description: what is it about
    type_: what kind of option it is
    regex: the regex pattern that will be used to extract the feature/cleaning option from tweet
    keep: concerns cleaning: keep feature or remove
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description


class CleaningOption(Option):
    """
    Represents either a cleaning option
    name: The name of the option
    description: what is it about
    type_: what kind of option it is
    regex: the regex pattern that will be used to extract the feature/cleaning option from tweet
    keep: concerns cleaning: keep feature or remove
    function: the function that takes as input a text and performs the cleaning - only for user added features
    """
    def __init__(self, name, description, regex, keep=False, function=None):
        super(CleaningOption, self).__init__(name, description)
        self.regex = regex
        self.keep = keep
        self.function = function


class FeatureOption(Option):
    """
    Represents either a feature option
    name: The name of the option
    description: what is it about
    type_: what kind of option it is
    regex: the regex pattern that will be used to extract the feature/cleaning option from tweet
    post_clean: whether lean_text or initial text will be used to extract the desired feature
    function: the function that takes as input a text and performs the feature extraction - only for user added features
    """
    def __init__(self, name, description="", regex="", post_clean=False, function=None):
        super(FeatureOption, self).__init__(name, description)
        self.regex = regex
        self.post_clean = post_clean
        self.function = function



class CleaningOptions(Options):
    """
    What to remove from tweet
    """
    cleaning_features = None

    def __init__(self):
        super(CleaningOptions, self).__init__()
        self.clean = True
        self.additional_stop_words = []
        self.set_defaults()

    def set_defaults(self):
        """
        Cleaning actions with the order they must be performed.
        :return: None
        :rtype: None
        """
        self.remove_non_ascii = CleaningOption("remove_non_ascii", True, regex="")
        self.remove_rt = CleaningOption("remove_rt", True, regex="")
        self.remove_laugh = CleaningOption("remove_laugh", True, regex="")
        self.split_sentences = CleaningOption("split_sentences", True, regex="")
        self.remove_negations = CleaningOption("remove_negations", True, regex="")
        self.remove_urls = CleaningOption("remove_urls", True, regex="")
        self.remove_emoticons = CleaningOption("remove_emoticons", True, regex="")
        self.remove_reference = CleaningOption("remove_reference", True, regex="")
        self.remove_special_characters = CleaningOption("remove_special_characters", True, regex="")
        self.fix_space = CleaningOption("fix_space", True, regex="")
        self.split_words = CleaningOption("split_words", True, regex="")
        self.convert_to_lower = CleaningOption("convert_to_lower", True, regex="")
        self.remove_multiples = CleaningOption("remove_multiples", True, regex="")
        self.remove_stop_words = CleaningOption("remove_stop_words", True, regex="")
        self.additional_stop_words = g.mysql_conn.execute_query(g.select_from_stop_words())

    def remove_option(self, name):
        pass


class FeatureOptions(Options):
    FeatureDataType = Globals.enum(Boolean=0, BooleanText=1, Decimal=2, Text=3)
    FeatureTypes = Globals.enum(Morphological=0, Figurative=1, PriorPolarity=2, Others=3)
    MorphFeatures = Globals.enum(__CAPITAL__=0, __HT__=1, __HT_POS__=2, __HT_NEG__=3, __LINK__=4, __POS_SMILEY__=5,
                                 __NEG_SMILEY__=6, __NEGATION__=7, __REFERENCE__=8, __RT__=9, __LAUGH__=10,
                                 __LOVE__=11, __OH_SO__=12, __DONT_YOU__=13, __AS_GROUND_AS_VEHICLE__=14,
                                 __questionmark__=15, __fullstop__=16, __exclamation__=17)
    _link_pattern = g.LINK_PATTERN
    _pos_smiley_pattern = g.POS_SMILEY_PATTERN
    _neg_smiley_pattern = g.NEG_SMILEY_PATTERN
    _negation_pattern = g.NEGATIONS_PATTERN
    _reference_pattern = g.REFERENCE_PATTERN
    _ht_pattern = g.HT_PATTERN
    _rt_pattern = g.RT_PATTERN
    _laugh_pattern = g.LAUGH_PATTERN
    _love_pattern = g.LOVE_PATTERN
    _capital_pattern = g.CAPITALS_PATTERN
    _oh_so_pattern = g.OH_SO_PATTERN
    _dont_you_pattern = g.DONT_YOU_PATTERN
    _as_ground_as_vehicle_pattern = g.AS_GROUND_AS_VEHICLE_PATTERN
    _questionmark_pattern = "\?"
    _fullstop_pattern = "\."
    _exclamation_pattern = "!"

    _patterns = {
        MorphFeatures.__CAPITAL__: _capital_pattern,
        MorphFeatures.__HT__: _ht_pattern,
        MorphFeatures.__LINK__: _link_pattern,
        MorphFeatures.__POS_SMILEY__: _pos_smiley_pattern,
        MorphFeatures.__NEG_SMILEY__: _neg_smiley_pattern,
        MorphFeatures.__NEGATION__: _negation_pattern,
        MorphFeatures.__REFERENCE__: _reference_pattern,
        MorphFeatures.__RT__: _rt_pattern,
        MorphFeatures.__LAUGH__: _laugh_pattern,
        MorphFeatures.__LOVE__: _love_pattern,
        MorphFeatures.__OH_SO__: _oh_so_pattern,
        MorphFeatures.__DONT_YOU__: _dont_you_pattern,
        MorphFeatures.__AS_GROUND_AS_VEHICLE__: _as_ground_as_vehicle_pattern,
        MorphFeatures.__questionmark__: _questionmark_pattern,
        MorphFeatures.__fullstop__: _fullstop_pattern,
        MorphFeatures.__exclamation__: _exclamation_pattern,
    }
    _tags = {
        MorphFeatures.name[MorphFeatures.__CAPITAL__]: "False",
        MorphFeatures.name[MorphFeatures.__HT__]: "False",
        MorphFeatures.name[MorphFeatures.__HT_POS__]: "False",
        MorphFeatures.name[MorphFeatures.__HT_NEG__]: "False",
        MorphFeatures.name[MorphFeatures.__LINK__]: "False",
        MorphFeatures.name[MorphFeatures.__POS_SMILEY__]: "False",
        MorphFeatures.name[MorphFeatures.__NEG_SMILEY__]: "False",
        MorphFeatures.name[MorphFeatures.__NEGATION__]: "False",
        MorphFeatures.name[MorphFeatures.__REFERENCE__]: "False",
        MorphFeatures.name[MorphFeatures.__RT__]: "False",
        MorphFeatures.name[MorphFeatures.__LAUGH__]: "False",
        MorphFeatures.name[MorphFeatures.__LOVE__]: "False",
        MorphFeatures.name[MorphFeatures.__OH_SO__]: "False",
        MorphFeatures.name[MorphFeatures.__DONT_YOU__]: "False",
        MorphFeatures.name[MorphFeatures.__AS_GROUND_AS_VEHICLE__]: "False",
        MorphFeatures.name[MorphFeatures.__questionmark__]: "False",
        MorphFeatures.name[MorphFeatures.__fullstop__]: "False",
        MorphFeatures.name[MorphFeatures.__exclamation__]: "False"
    }

    features_descr = {
        "__OH_SO__": "Looks for Oh, so * pattern e.g. ",
        "__DONT_YOU__": "Looks for Don*t you * pattern e.g. ",
        "__AS_GROUND_AS_VEHICLE__": "Looks for as * as * pattern e.g.:",
        "__CAPITAL__": "Presence of CAPITALIZED words -- indicates heightened emotion ",
        "__HT__" : "",
        "__HT_POS__": "",
        "__HT_NEG__": "",
        "__LINK__": "Presence/Absence of ulrs",
        "__POS_SMILEY__": "",
        "__NEG_SMILEY__": "",
        "__NEGATION__": "Presense/Absense of negations e.g. I __LOVE__ working at weekends#NOT or I don't __LOVE__ working at weekends.",
        "__REFERENCE__": "@user",
        "__questionmark__": "Presense/Absense of ?",
        "__exclamation__": "Presense/Absense of !",
        "__fullstop__": "Presense/Absense of .",
        "__RT__": "Presense/Absense of __RT__",
        "__LAUGH__": "Presense/Absense of __LAUGH__ patterns",
        "__LOVE__": "Presense/Absense of <3",
        "__res__": "Calculate Resnik Text Similarity Measure. [0,1]",
        "__lin__": "Calculate Lin Text Similarity Measure.",
        "__wup__": "Calculate Wup Text Similarity Measure.",
        "__path__": "Calculate Path Text Similarity Measure.",
        "__postags__": "POS-Tag tweet.",
        "__swn_score__": "Calculate total SentiWordNet Score for Tweet",
        "__s_word__": "SentiWordNet score for each word, e.g. s_word-{index of word in tweet} s_word-1 : 1.2",
        "__contains_": "contains_{word}: True/False",
    }

    feature_type = {
        "__OH_SO__": FeatureTypes.Figurative,
        "__DONT_YOU__": FeatureTypes.Figurative,
        "__AS_GROUND_AS_VEHICLE__": FeatureTypes.Figurative,
        "__CAPITAL__": FeatureTypes.Morphological,
        "__HT__": FeatureTypes.Morphological,
        "__HT_POS__": FeatureTypes.Morphological,
        "__HT_NEG__": FeatureTypes.Morphological,
        "__LINK__": FeatureTypes.Morphological,
        "__POS_SMILEY__": FeatureTypes.Morphological,
        "__NEG_SMILEY__": FeatureTypes.Morphological,
        "__NEGATION__": FeatureTypes.Morphological,
        "__REFERENCE__": FeatureTypes.Morphological,
        "__questionmark__": FeatureTypes.Morphological,
        "__exclamation__": FeatureTypes.Morphological,
        "__fullstop__": FeatureTypes.Morphological,
        "__RT__": FeatureTypes.Morphological,
        "__LAUGH__": FeatureTypes.Morphological,
        "__LOVE__": FeatureTypes.Morphological,
        "__res__": FeatureTypes.Figurative,
        "__lin__": FeatureTypes.Figurative,
        "__wup__": FeatureTypes.Figurative,
        "__path__": FeatureTypes.Figurative,
        "__postags__": FeatureTypes.Morphological,
        "__swn_score__": FeatureTypes.PriorPolarity,
        "__s_word__": FeatureTypes.PriorPolarity,
        "__contains_": FeatureTypes.Morphological,
    }

    def __init__(self):
        super(Options, self).__init__()
        self.get_features = True
        self.feature_options = []
        self.extra_options = []
        self.set_defaults()

    def set_defaults(self):
        for feature, descr in self.features_descr.items():
            self.feature_options.append(FeatureOption(feature,              # name
                                        descr,                       # description
                                        self.feature_type[feature],  # type
                                        self._tags[feature] if feature in self._tags else None  # regex
                                        ))

    def get_feature_by_name(self, name):
        for feat in self.feature_options:
            if feat.name == name:
                return feat
        return None

    def set_regex_pattern(self, feature_name, pattern):
        for feature in self.feature_options:
            if feature.name == feature_name:
                feature.regex = pattern
                return
        raise Exception("Feature {0} not in feature list".format(feature_name))

    def set_discretization(self, feature_name, discretization):
        for feature in self.feature_options:
            if feature.name == feature_name:
                feature.discretization = discretization
                return
        raise Exception("Feature {0} not in feature list".format(feature_name))

    def add_feature(self, feature_option):
        if not isinstance(feature_option, Option):
            raise Exception("Feature is not instance of Option")
        self.extra_options.append(feature_option)

    def remove_feature_by_name(self, feature_name):
        for feature in self.feature_options:
            if feature.name == feature_name:
                del self.feature_options[feature_name]
                return True
        raise Exception("Feature {0} not in feature list".format(feature_name))

    def get_tags(self):
        return self._tags

    def get_patterns(self):
        return self._patterns
