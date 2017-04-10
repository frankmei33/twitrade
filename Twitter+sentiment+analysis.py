import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# coding: utf-8

# In[1]:

# List containing positive adn negative tweets
from nltk.corpus import twitter_samples
pos=twitter_samples.strings('positive_tweets.json')
neg=twitter_samples.strings('nagative_tweets.json')

def review_cleaner(review):
    review = re.sub('[^a-zA-Z]',' ',review)
    review = word_tokenize(review.lower())
    eng_stopwords = set(stopwords.words("english"))
    review = [w for w in review if not w in eng_stopwords]
    review = ' '.join(review)
    return(review)

for i in range(0,len(pos)):
    pos[i]=review_cleaner(pos[i])
    
for i in range(0,len(neg)):
    neg[i]=review_cleaner(neg[i])

pos_tweets = []
for i in range(0,len(pos)):
    pos_tweets.append((pos[i],'positive'))
    
neg_tweets = []
for i in range(0,len(neg)):
    neg_tweets.append((neg[i],'negative'))


# In[3]:

# Take both lists and create a single list of tuples 
# each containing two elements. First element is an array 
# containing the words and second element is the type of sentiment. 
# Get rid of the words smaller than 2 characters and we use lowercase for everything.

tweets = []
for (words, sentiment) in pos_tweets + neg_tweets:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
    tweets.append((words_filtered, sentiment))


# In[4]:

tweets


# In[5]:

# Test tweets

test_tweets = [(['feel', 'happy', 'this', 'morning'], 'positive'),
               (['larry', 'friend'], 'positive'),
               (['not', 'like', 'that', 'man'], 'negative'),
               (['house', 'not', 'great'], 'negative'),
               (['your', 'song', 'annoying'], 'negative')]


# In[6]:

test_tweets


# ## Classifier

# In[9]:

import nltk


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words
    
def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(tweets))


# In[16]:

nltk.FreqDist(get_words_in_tweets(tweets))


# As you can see, ‘this’ is the most used word in our tweets, 
# followed by ‘car’, followed by ‘concert’…
# 
# To create a classifier, we need to decide what features are relevant. 
# To do that, we first need a feature extractor. Use on that returns a dictionary indicating what words are contained in the input passed. 
# Here, the input is the tweet. Use the word features list defined above along with the 
# input to create the dictionary.

# In[17]:

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


# In[26]:

# As an example, call the feature extractor with the document 
# [‘love’, ‘this’, ‘car’] which is the first positive tweet. 
# We obtain the following dictionary which indicates that the document 
# contains the words: ‘love’, ‘this’ and ‘car’.

    
extract_features(['love', 'this', 'car'])


# In[29]:

# apply feature extractor to the training set

training_set = nltk.classify.apply_features(extract_features, tweets)


# In[31]:

# train the classifier with the training set

classifier = nltk.NaiveBayesClassifier.train(training_set)


# In[41]:

#save trained classifier
import pickle
f = open('sentiment_classifier.pickle', 'wb')
pickle.dump(classifier, f)
f.close()

# In[ ]:

tweet = 'Larry is my friend'
print (classifier.classify(extract_features(tweet.split())))


# In[ ]:

tweet = 'Your friend is annoying'
print (classifier.classify(extract_features(tweet.split())))


# In[ ]:

tweet = 'My house is not great'
print (classifier.classify(extract_features(tweet.split())))

