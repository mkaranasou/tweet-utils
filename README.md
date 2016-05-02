# tweet-utils
##HOW TO and useful information
###Simple Example
```python
from TweetUtils import TweetUtils
from TweetUtils.models.Config import Config

utils = TweetUtils(Config(True, True))

tweet_list = utils.process(["This is lovely!!!#NOT", "I hate Monday mornings..."])
single_tweet = utils.process("This is lovely!!!#NOT")
```
### Adding Features Example
#### This works like callbacks in Javascript
```python
from TweetUtils import TweetUtils
from TweetUtils.models.Config import Config

def pre_clean_function(text):
    print "pre_clean_function", text
    return "new pre-clean feature added"


def post_clean_function(text):
    print "post_clean_function", text
    return "new post-clean feature added"

# create a Config object with both cleaning and feature extraction set to True
utils_cfg = Config(True, True)
# Add a new FeatureOption giving your function as a parameter. Your function should take a string as an input.
# as shown above. You can choose that the function is excecuted on the original tweet text or the text 
# that is left after the cleaning.
utils_cfg.feature_options.add_feature(FeatureOption("test", function=pre_clean_function))
utils_cfg.feature_options.add_feature(FeatureOption("test", post_clean=True, function=post_clean_function))
utils = TweetUtils(utils_cfg)

# proceed with processing
tweet_list = utils.process(["This is lovely!!!#NOT", "I hate Monday mornings..."])
single_tweet = utils.process("This is lovely!!!#NOT")

```

## Furure Work
* Detach from MySQL and find another way to store and access SentiWordNet and stop-words 
 (maybe in-memory if it is not a big overhead or consider sqlite).
* Add more features and make feature extraction extensible
* Detach from globals because database access in multiprocessing has issues when it comes to concurrency.
