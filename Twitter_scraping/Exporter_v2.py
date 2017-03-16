# -*- coding: utf-8 -*-

# v2 update: modified the structure of the code.
# Now search all the tweets from the date specified by "since" and "until"(not included)
# and save each day's tweets as a csv in a directory named with the search query
# (all in lower cases).
#
# Note: now only supports usage like this example:
# 	python Exporter_v2.py --querysearch "nasdaq" --since 2015-01-01 --until 2015-01-10
#
# TODO: 
#	add sentiment analysis

import sys,getopt,got3,datetime,codecs
import os
import multiprocessing
import pandas as pd


def run_query_search(query, since, until):
	tweetCriteria = got3.manager.TweetCriteria()

	tweetCriteria.since = since
	tweetCriteria.until = until
	tweetCriteria.querySearch = query
			
	outputName = tweetCriteria.querySearch + "_" + since + '.csv'
	outputFile = codecs.open(query + '/' + outputName, "w+", "utf-8")
	
	outputFile.write('username,date,retweets,favorites,text,geo,mentions,hashtags,id,permalink,verified')
	
	print('Searching date: ', since)
	
	def receiveBuffer(tweets):
		for t in tweets:
			outputFile.write(('\n%s,%s,%d,%d,"%s",%s,%s,%s,"%s",%s,%s' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink, t.verified)))
		outputFile.flush();
		# print(t.date)
		# print('More %d saved on file...\n' % len(tweets))
	
	got3.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)
	
	outputFile.close()
	print('Done. Output file generated %s.' % (query + '/' + outputName))



def main(argv):

	if len(argv) == 0:
		print('You must pass some parameters. Use \"-h\" to help.')
		return
		
	if len(argv) == 1 and argv[0] == '-h':
		print("""\nThis is the Twitter scraping function.
Example usage:
	python Exporter_v2.py --querysearch "TSLA" --since 2015-01-01 --until 2015-01-10\n""")
		return

	try: 
		opts, args = getopt.getopt(argv, "", ("since=", "until=", "querysearch="))
		
		for opt,arg in opts:
			if opt == '--since':
				main_since = arg
				
			elif opt == '--until':
				main_until = arg
				
			elif opt == '--querysearch':
				query = arg.lower() # all to lower case

		# store all the csv data in a direcory named with the query
		if not os.path.isdir(query):
			os.mkdir(query)

		all_dates = pd.date_range(start=main_since, end=main_until, freq='D')
		print('Searching Query: ', query)
		print('Since: ', main_since)
		print('Until: ', main_until)
		print('Total number of days to search: ', len(all_dates)-1, '\n')

		# start scraping
		jobs = []
		for i in range(len(all_dates)-1):
			since = all_dates[i].strftime("%Y-%m-%d")
			until = all_dates[i+1].strftime("%Y-%m-%d")
			p = multiprocessing.Process(target=run_query_search, args=(query, since, until,))
			# run_query_search(query, since, until)
			jobs.append(p)
			p.start()

	except arg:
		print('Arguments parser error, try -h' + arg)

if __name__ == '__main__':
	main(sys.argv[1:])

