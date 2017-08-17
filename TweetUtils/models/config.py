from TweetUtils.models.options import CleaningOptions, FeatureOptions

__author__ = 'maria'


class Config(object):
    """
    Configuration for cleaning and feature extraction.
    Loaded with defaults for both.
    Options can be modified for both cleaning_options and feature_options afterwards
    """
    def __init__(self, clean=True, get_features=True):
        if not clean and not get_features:
            raise Exception("Configuration is not valid!")
        if clean:
            self.cleaning_options = CleaningOptions()
        else:
            self.cleaning_options = None

        if get_features:
            self.feature_options = FeatureOptions()
        else:
            self.feature_options = None

