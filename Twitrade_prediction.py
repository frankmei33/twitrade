import pandas as pd
import os,sys,glob
from review_cleaner import review_cleaner
from review_cleaner import extract_features
import pickle
import datetime
from Twitter_scraping.got3.manager import TweetManager, TweetCriteria
from stock_price import stock_price
from sklearn.ensemble import RandomForestClassifier

def main(argv):

	if len(argv) != 1:
		print('The number of parameters is incorrect. Input the keywords you want to search.')
		return  
	keyword = argv[0]
	
	print('Get tweets...')
	df = get_train(keyword)
	l = df.shape[0]-1
	print('Get price...')
	price = get_price(keyword, l)
	
	train_df = pd.merge(df, price, on='date')
	train_df = train_df.dropna(axis=0)
	train_df = train_df[['date', 'retweets', 'retweets_3d', 'retweets_5d', 'favorites', 'favorites_3d', 'favorites_5d',
						   'hashtags', 'mentions', 'sentiment', 'price', 'diff_1d', 'diff_3d', 'diff_5d']]
	l = train_df.shape[0]-1
	
	#train data with random forest
	print('Training...')
	forest = RandomForestClassifier(n_estimators = 50)
	forest = forest.fit(train_df.iloc[0:(l-1),1:11], train_df['diff_1d'][0:(l-1)])
	pred1 = forest.predict(train_df.iloc[(l-1):l,1:11])
	print('This stock value will likely to', 'drop' if pred1[0]==0 else 'increase', 'in the next day.')

	forest = RandomForestClassifier(n_estimators = 50)
	forest = forest.fit(train_df.iloc[0:(l-3),1:11], train_df['diff_3d'][0:(l-3)])
	pred3 = forest.predict(train_df.iloc[(l-1):l,1:11])
	print('This stock value will likely to', 'drop' if pred3[0]==0 else 'increase', 'in the following 3 days.')

	forest = RandomForestClassifier(n_estimators = 50)
	forest = forest.fit(train_df.iloc[0:(l-5),1:11], train_df['diff_5d'][0:(l-5)])
	pred5 = forest.predict(train_df.iloc[(l-1):l,1:11])
	print('This stock value will likely to', 'drop' if pred5[0]==0 else 'increase', 'in the next week.')
	
	if (pred1 + pred3 + pred5 > 1.5):
		print('Overall, recommend buying in.')
	else:
		print('Overall, recomment selling out.')

#get training dataset
def get_train(keyword):
	#check database for existing files
	os.chdir('data/')
	file = [f for f in os.listdir() if keyword in f]
	
	if file != []:
		
		tw_old =  pd.read_csv(file[0])
		tw_old.date = pd.to_datetime(tw_old.date)
		
		last = tw_old.loc[len(tw_old)-1, 'date'].strftime("%Y-%m-%d")
		since = (datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")

		if (last == since):
			final = tw_old

		else:
			#new data
			until = (datetime.date.today()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
			tw_new = get_data(keyword, since, until)
		
			#Since twitter scrape searches for tweets by utc time, the first and last day's tweets are incomplete,
			#thus discard first and last row
			tw_new = tw_new.loc[1:len(tw_new)-2,]
		
			#merge with existing data
			final = pd.concat([tw_old, tw_new], ignore_index=True)

			#manually add moving average for the new data
			loc=final.shape[0]-1
			final.loc[loc,'retweets_3d'] = (final.loc[loc,'retweets']+final.loc[loc-1,'retweets']+final.loc[loc-2,'retweets'])/3
			final.loc[loc,'retweets_5d'] = (final.loc[loc,'retweets_3d']*3+final.loc[loc-3,'retweets']+final.loc[loc-4,'retweets'])/5
			final.loc[loc,'favorites_3d'] = (final.loc[loc,'favorites']+final.loc[loc-1,'favorites']+final.loc[loc-2,'favorites'])/3
			final.loc[loc,'favorites_5d'] = (final.loc[loc,'favorites_3d']*3+final.loc[loc-3,'favorites']+final.loc[loc-4,'favorites'])/5
		
	else:
		since = (datetime.date.today()-datetime.timedelta(days=106)).strftime("%Y-%m-%d")
		until = (datetime.date.today()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
		tw_new = get_data(keyword, since, until)
		final = tw_new.loc[1:len(tw_new)-2,]
		final = movingaverage(final)

	return(final)


#get history stock price
def get_price(keyword, length):
	until = datetime.date.today().strftime("%Y-%m-%d")
	since = (datetime.date.today()-datetime.timedelta(days=length)).strftime("%Y-%m-%d")
	price = stock_price.get_price(keyword, since, until)

	price.columns = ['date','price']
	price.date = pd.to_datetime(price.date)
	price.price = price.price.astype(float)
	price = price.sort_values(by='date')
	price['diff_1d'] = (price.price - price.price.shift(1)).shift(-1)
	price['diff_3d'] = (price.price - price.price.shift(3)).shift(-3)
	price['diff_5d'] = (price.price - price.price.shift(5)).shift(-5)
	price['diff_1d'] = [1 if d > 0 else 0 for d in price['diff_1d']]
	price['diff_3d'] = [1 if d > 0 else 0 for d in price['diff_3d']]
	price['diff_5d'] = [1 if d > 0 else 0 for d in price['diff_5d']]

	return(price)


#scrape the data from Twitter_scraping 
def get_data(keyword, since, until):
	lst = []

	tweetCriteria = TweetCriteria()
	tweetCriteria.since = since
	tweetCriteria.until = until
	tweetCriteria.querySearch = keyword
	tweetCriteria.setLang('en')

	def receiveBuffer(tweets):
		for t in tweets:
			lst.append([t.username, (t.date+datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.mentions, t.hashtags, t.verified])

	tweets = TweetManager.getTweets(tweetCriteria, receiveBuffer)
	
	df = pd.DataFrame(lst, columns=['username','date','retweets','favorites','text','mentions','hashtags','verified'])
	df = clean(df)
	return(df)

#cleaning data
def clean(df):
	df.mentions = df.mentions.str.count('@')
	df.hashtags = df.hashtags.str.count('#')
	df.date = pd.to_datetime(df.date)
	df = df.sort_values(by='date')
	df.date = pd.DatetimeIndex(df.date).normalize()   
	df['sentiment'] = df.text.apply(review_cleaner)
	df['verified'] = [0 if pd.isnull(t) else 1 for t in df.verified]
	for i in range(0,df.shape[0]):
		s = classifier.classify(extract_features(word_features, df.sentiment[i].split()))
		df.loc[i,'sentiment'] = 1 if s == 'positive' else 0
	df['sentiment'] = df['sentiment'].astype(str).astype(int)
	
	df1=df[['date','retweets','favorites','mentions','hashtags','verified','sentiment']]
	df1.loc[:,'retweets'] = df1['retweets'] * (df1['verified']*5+1) * (df1['sentiment']*2-1)
	df1.loc[:,'favorites'] = df1['favorites'] * (df1['verified']*5+1) * (df1['sentiment']*2-1)
	df1.loc[:,'mentions'] = df1['mentions'] * (df1['verified']*5+1) * (df1['sentiment']*2-1)
	df1.loc[:,'hashtags'] = df1['hashtags'] * (df1['verified']*5+1) * (df1['sentiment']*2-1)
	
	grouped = df1.groupby('date',as_index=False)
	df2 = grouped.agg({'retweets':'sum', 'favorites':'sum','mentions':'sum', 'hashtags':'sum', 
					   'sentiment':'mean'})
	return(df2)

#add moving average data
def movingaverage(df):
	df.loc[:,'retweets_3d'] = (df['retweets'] + df['retweets'].shift(1) + df['retweets'].shift(2))/3
	df.loc[:,'retweets_5d'] = (df['retweets_3d']*3 + df['retweets'].shift(3) + df['retweets'].shift(4))/5
	df.loc[:,'favorites_3d'] = (df['favorites'] + df['favorites'].shift(1) + df['favorites'].shift(2))/3
	df.loc[:,'favorites_5d'] = (df['favorites_3d']*3 + df['favorites'].shift(3) + df['favorites'].shift(4))/5
	finaldata = df.dropna(axis=0)
	finaldata = finaldata[['date', 'retweets', 'retweets_3d', 'retweets_5d', 'favorites', 'favorites_3d', 'favorites_5d',
						   'hashtags', 'mentions', 'sentiment']]
	return(finaldata)


if __name__ == '__main__':
	#load trained sentiment classifier and features
	with open('sentiment_classifier.pickle', 'rb') as f:
		classifier = pickle.load(f)
	with open('feature.pickle', 'rb') as f:
		word_features = pickle.load(f)

	main(sys.argv[1:])




