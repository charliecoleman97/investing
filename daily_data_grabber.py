from datetime import date
import pandas as pd
import variables
import os
from os import listdir
from os.path import isfile, join
'''
This script will update all the stocks CSVs with daily stock data - works better than having to redownload the
CSVs again each time to update them. It will also add Span A, Span B columns as well
'''
# get Path to csv
PATH = variables.stocks

# Get todays date
today = date.today()

# Get Dataframes from csv
def get_stock_df_from_csv(ticker):
    try:
        df = pd.read_csv(PATH + ticker + ".csv", index_col=0)
    except FileNotFoundError:
        print("File is not here" )
        print('Expected file: ' + PATH + ticker + ".csv")
    else: 
        return df 

# Get all stock tickers
files = [x for x in os.listdir(PATH) if os.path.isfile(os.path.join(PATH, x))]
tickers = [os.path.splitext(x)[0] for x in files]
# tickers.remove('.ds_Store')

tickers.sort()
len(tickers)

# We want to find the last row in the dataframe (most recent date) and store it as
# dataframe 

