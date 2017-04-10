
# coding: utf-8

# In[1]:

# List containing positive tweets
pos_tweets = [('I love this car', 'positive'),
              ('This view is amazing', 'positive'),
              ('I feel great this morning', 'positive'),
              ('I am so excited about the concert', 'positive'),
              ('He is my best friend', 'positive')]


# In[2]:

# List containing negative tweets
neg_tweets = [('I do not like this car', 'negative'),
              ('This view is horrible', 'negative'),
              ('I feel tired this morning', 'negative'),
              ('I am not looking forward to the concert', 'negative'),
              ('He is my enemy', 'negative')]


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

#print (classifier.show_most_informative_features(32))


# In[ ]:

tweet = 'Larry is my friend'
print (classifier.classify(extract_features(tweet.split())))


# In[ ]:

tweet = 'Your friend is annoying'
print (classifier.classify(extract_features(tweet.split())))


# In[ ]:

tweet = 'My house is not great'
print (classifier.classify(extract_features(tweet.split())))

