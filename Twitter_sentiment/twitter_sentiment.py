import review_cleaner
import nltk

# List containing positive adn negative tweets
print('Loading training set...')
from nltk.corpus import twitter_samples
pos=twitter_samples.strings('positive_tweets.json')
neg=twitter_samples.strings('negative_tweets.json')

pos_tweets = []
for i in range(0,len(pos)):
    pos_tweets.append((review_cleaner.review_cleaner(pos[i]),'positive'))
    
neg_tweets = []
for i in range(0,len(neg)):
    neg_tweets.append((review_cleaner.review_cleaner(neg[i]),'negative'))

# Take both lists and create a single list of tuples 
# each containing two elements. First element is an array 
# containing the words and second element is the type of sentiment. 
# Get rid of the words smaller than 2 characters and we use lowercase for everything.

tweets = []
for (words, sentiment) in pos_tweets + neg_tweets:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
    tweets.append((words_filtered, sentiment))


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words
    
def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    wordlist = {k:v for (k,v) in wordlist.items() if v > 5}
    word_features = list(wordlist.keys())
    return word_features

word_features = get_word_features(get_words_in_tweets(tweets))

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

print('Training...')
# apply feature extractor to the training set
training_set = nltk.classify.apply_features(extract_features, tweets)

# train the classifier with the training set
classifier = nltk.NaiveBayesClassifier.train(training_set)

print('Saving classifier and features...')
#save trained classifier
import pickle
with open('sentiment_classifier.pickle', 'wb') as f:
    pickle.dump(classifier, f)

with open('feature.pickle', 'wb') as f:
    pickle.dump(word_features, f)

print('Classifier built and saved. Done!')