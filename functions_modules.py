import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import time


# DOWNLOAD FUNCTIONS 

def get_column_from_csv(file, col_name):
    ''' Retrieves ticker names from CSV'''
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print("File does not exist")
    else:
        return df[col_name]

def save_to_csv_from_yahoo(folder, ticker):
    '''Downloads Ticker data from yfinance and saves as CSV'''
    stock = yf.Ticker(ticker)

    try:
        print("Get Data for: ", ticker)
        # Get historical closing price data 
        df = stock.history(period="5y")

        # Wait  2 seconds
        time.sleep(2)

        # Remove the period for saving the file name
        # Save data to a CSV file 
        # File to save to 
        the_file = folder + ticker.replace(".", "_") + '.csv'
        print(the_file, " Saved")
        df.to_csv(the_file)

    except Exception as ex:
        print("Couldn't Get Data :", ticker)

# CALCULATION FUNCTIONS 

def add_daily_return_to_df(df):
    '''Adds daily returns column to df'''
    df['daily_return'] = (df['Close'] / df['Close'].shift(1)) - 1
    return df

def add_cum_return_to_df(df):
    '''Add cumulative return column to df'''
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    return df

def add_bollinger_bands(df):
    '''Adds lower, middle and upper bollinger band columns to df'''
    df['middle_band'] = df['Close'].rolling(window=20).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['Close'].rolling(window=20).std()
    return df

def add_Ichimoku(df):
    '''Adds the columns used for Ichimoku'''
    hi_val = df['High'].rolling(window=9).max()
    low_val = df['Low'].rolling(window=9).min()
    df['Conversion'] = (hi_val + low_val) / 2

    # Baseline
    hi_val2 = df['High'].rolling(window=26).max()
    low_val2 = df['Low'].rolling(window=26).min()
    df['Baseline'] = (hi_val2 + low_val2) / 2

    # Spans
    df['SpanA'] = ((df['Conversion'] + df['Baseline']) / 2).shift(26)
    hi_val3 = df['High'].rolling(window=52).max()
    low_val3 = df['Low'].rolling(window=52).min()
    df['SpanB'] = ((hi_val3 + low_val3) / 2).shift(26)
    df['Lagging'] = df['Close'].shift(-26)

    return df

# PLOTTING FUNCTIONS

def plot_with_boll_bands(df, ticker):
    '''Plots graph with bollinger bands'''
    fig = go.Figure()

    candle = go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
    low=df['Low'], close=df['Close'], name='Candlestick')

    upper_line = go.Scatter(x=df.index, y=df['upper_band'], 
    line=dict(color='rgba(250, 0, 0, 0.75)', 
    width=1), name='Upper Band')

    mid_line = go.Scatter(x=df.index, y=df['middle_band'], 
    line=dict(color='rgba(0, 0, 250, 0.75)', 
    width=1), name='Middle Band')

    lower_line = go.Scatter(x=df.index, y=df['lower_band'], 
    line=dict(color='rgba(0, 250, 0, 0.75)', 
    width=1), name='Lower Band')

    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(mid_line)
    fig.add_trace(lower_line)

    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")

    fig.update_layout(title=ticker + " Bollinger Bands", 
    height=800, width=1700, showlegend=True)
    fig.show()

def get_fill_color(label):
    '''Adds fill colour for Ichimoku plot'''
    if label >= 1:
        return 'rgba(0,250,0,0.4)'
    else:
        return 'rgba(250,0,0,0.4)'

def get_Ichimoku(df):
    '''Plots Ichimoku graph'''
    candle = go.Candlestick(x=df.index, open=df['Open'],
    high=df['High'], low=df["Low"], close=df['Close'], name="Candlestick")

    df1 = df.copy()
    fig = go.Figure()
    df['label'] = np.where(df['SpanA'] > df['SpanB'], 1, 0)
    df['group'] = df['label'].ne(df['label'].shift()).cumsum()

    df = df.groupby('group')

    dfs = []
    for name, data in df:
        dfs.append(data)

    for df in dfs:
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanA,
        line=dict(color='rgba(0,0,0,0)')))

        fig.add_traces(go.Scatter(x=df.index, y=df.SpanB,
        line=dict(color='rgba(0,0,0,0)'),
        fill='tonexty',
        fillcolor=get_fill_color(df['label'].iloc[0])))

    baseline = go.Scatter(x=df1.index, y=df1['Baseline'], 
    line=dict(color='pink', width=2), name="Baseline")

    conversion = go.Scatter(x=df1.index, y=df1['Conversion'], 
    line=dict(color='black', width=1), name="Conversion")

    lagging = go.Scatter(x=df1.index, y=df1['Lagging'], 
    line=dict(color='purple', width=2), name="Lagging")

    span_a = go.Scatter(x=df1.index, y=df1['SpanA'], 
    line=dict(color='green', width=2, dash='dot'), name="Span A")

    span_b = go.Scatter(x=df1.index, y=df1['SpanB'], 
    line=dict(color='red', width=2, dash='dot'), name="Span B")

    fig.add_trace(candle)
    fig.add_trace(baseline)
    fig.add_trace(conversion)
    fig.add_trace(lagging)
    fig.add_trace(span_a)
    fig.add_trace(span_b)
    
    fig.update_layout(height=800, width=1700, showlegend=True)

    fig.show()

