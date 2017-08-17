# tweet-utils
A library to help with the feature extraction process on tweets for the purpose of Sentiment Analysis.

HOW TO and useful information
---
### Simple Example
```python
from TweetUtils import TweetUtils
from TweetUtils.models.Config import Config

utils = TweetUtils(Config(True, True))

tweet_list = utils.process(["This is lovely!!!#NOT", "I hate Monday mornings..."])
single_tweet = utils.process("This is lovely!!!#NOT")
```
### Adding Features Example
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

### Multiprocessing example
Since tweets are independend of each other (at least in simple cases), we can parallelize the processing.
A simple example would be something like this:

```python
# create a function to be executed by each process
def process(tweet_tuple):
    global processed
    try:
        # create a TweetUtils instance and process the tweet
        utils = TweetUtils(Config(True, True))
        tweet = utils.process(tweet_tuple[1].strip())
        # update the tweet in database
        mysql_conn.update(q_update.format(str(tweet.feature_dict), tweet_tuple[0]))
    except:
        # something went wrong, log it
        print tweet_tuple
        logger.error(tweet_tuple)

    processed += 1
    # print process every 1000 of tweets
    if processed % 1000 == 0:
        print processed, datetime.datetime.now()

if __name__ == "__main__":
    # keep a global count to know how things are going
    processed = 0

    # This is a very simple example that just fetches tweets from a MySQL
    # with raw SQL queries, to feed them to the processing module
    # and update the database with the results.
    # set the queries to retrieve and update the tweets
    q ="SELECT id, text FROM TweetDb.tweet_data;"
    q_update = """UPDATE TweetDb.tweet_data SET feature_dict="{0}" WHERE id="{1}";"""

    data = mysql_conn.execute_query(q)        # get the tweets
    print "start", datetime.datetime.now()
    pool = Pool(processes=2)
    pool.map(process, data)                     # begin
    print processed
    print "finished", datetime.datetime.now()
```

## Furure Work
* Detach from MySQL and find another way to store and access SentiWordNet and stop-words 
 (maybe in-memory if it is not a big overhead or consider sqlite).
* Add more features and make feature extraction extensible
* Detach from globals because database access in multiprocessing has issues when it comes to concurrency.
