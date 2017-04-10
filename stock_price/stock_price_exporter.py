#install yahoo_finance package
#	pip install yahoo_finance

from yahoo_finance import Share
import sys

stock_name = sys.argv[1] #stock symbol, e.g. TSLA
start_date = sys.argv[2] #format %Y-%m-%d
end_date = sys.argv[3] #formate %Y-%m-%d

yahoo = Share(stock_name)

import numpy as np
import pandas as pd

hist = yahoo.get_historical(start_date,end_date)
N = 2 
stock = pd.DataFrame(np.zeros(len(hist)*N).reshape(len(hist),N),columns=['Date','Close price'])
for i in range(0,len(hist)):
    stock.iloc[i,0] = hist[i]['Date']
    stock.iloc[i,1] = hist[i]['Close']

stock.to_csv(stock_name+'_'+start_date+'_'+end_date+'.csv',index = False)