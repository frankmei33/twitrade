import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def review_cleaner(review):
    m = re.search('(.+)http', review)
    if m:
        review = m.group(1)
    review = re.sub('#([^# ].)',r'\1',review)
    review = re.sub('[^a-zA-Z ][^ ]*',' ', review)
    review = word_tokenize(review.lower())
    eng_stopwords = set(stopwords.words("english"))
    review = [w for w in review if not w in eng_stopwords]
    review = ' '.join(review)
    return(review)

def extract_features(word_features, document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features
