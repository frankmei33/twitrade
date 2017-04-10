#install yahoo_finance package
#	pip install yahoo_finance

from yahoo_finance import Share
import sys
import numpy as np
import pandas as pd

def get_price(stock_name, start_date, end_date):
    yahoo = Share(stock_name)

    hist = yahoo.get_historical(start_date,end_date)
    N = 2 
    stock = pd.DataFrame(np.zeros(len(hist)*N).reshape(len(hist),N),columns=['Date','Close price'])
    for i in range(0,len(hist)):
        stock.iloc[i,0] = hist[i]['Date']
        stock.iloc[i,1] = hist[i]['Close']

    return(stock)

