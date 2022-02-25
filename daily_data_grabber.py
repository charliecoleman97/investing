from datetime import datetime, date, timedelta
import variables
import os
import yfinance as yf
import pandas as pd 
import functions as fn

'''
This script will update all the stocks CSVs with daily stock data - works better than having to redownload the
CSVs again each time to update them. It will also add Span A, Span B columns as well

Look at daily_data_grabber.ipynb for a more documented version of this script
'''
# get Path to csv
PATH = variables.stocks


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


count = 0 
for ticker in tickers:
    count += 1
    try: 
        old_df = get_stock_df_from_csv(ticker)
        start_date = (datetime.strptime(old_df.index[-1], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")

        new_df = yf.download(ticker, start=start_date, end=end_date)
        new_df = new_df.drop(columns="Adj Close")
        new_df = new_df.reset_index()
        new_df["Date"] = new_df["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
    
        old_df = old_df.reset_index()       

        final_df = old_df.append(new_df)
        final_df.set_index("Date")

        df = fn.add_daily_return_to_df(final_df)
        df = fn.add_cum_return_to_df(df)
        df = fn.add_bollinger_bands(df)
        df = fn.add_Ichimoku(df)   
        df.to_csv(PATH + ticker + '.csv')

    except Exception as ex:
        print(ex)
    
    print(f'{count}/{len(tickers)}')
