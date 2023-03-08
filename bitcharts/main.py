'''
Adapted from: How to Download Historical Price Data from Binance with Python
marketstack (62) in python •  9 months ago
https://steemit.com/python/@marketstack/how-to-download-historical-price-data-from-binance-with-python
'''
import requests        # for making http requests to binance
import json            # for parsing what binance sends back to us
import pandas as pd    # for storing and manipulating the data we get back
import numpy as np     # numerical python, i usually need this somewhere
                       # and so i import by habit nowadays

import matplotlib.pyplot as plt # for charts and such
import datetime as dt  # for dealing with times

INTERVAL = '1m'


class Chart:
  def __init__(self,coin='BTC',market='USDT',candles='30m'):
    '''Chart class. Handler for the creation of financial charts for cryptocurrencies and analysis thereof

    Parameters
    ----------
    coin : np.array(int)
        ticker name of quote currency (default: BTC)
    market : int / 'auto'(str)
        ticker name of base currency (default: USDT)
    candles : str
        time interval for candles (default: 30m)
    DATAFRAME : <pandas.DataFrame object>
        financial data of price activity loaded from above information.
    '''
    self.coin = coin
    self.market = market
    self.candles = candles
    self.DATAFRAME = []

  def get_bars(self):

    quote = self.coin + self.market
    interval = self.candles


    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + quote + '&interval=' + interval
    data = json.loads(requests.get(url).text)
    # print(data)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                  'o', 'h', 'l', 'c', 'v',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]

    self.DATAFRAME = df

    return df

  def coinpair(self):
      '''returns ohlc data of the quote cryptocurrency with
      the base currency (i.e. 'market'); base for alts must be either USDT or BTC'''
      quote = self.coin
      base = self.market
      interval = self.candles

      if quote == 'BTC':
        btcusd = 1
      elif base == 'USDT':
        self.coin = 'BTC'
        self.market = 'USDT'
        btcusd = self.get_bars()['c'].astype('float') 
      else:
        btcusd = 1

      self.market = 'USDT' if quote == 'BTC' else 'BTC'
      self.coin = quote

      df = self.get_bars()

      df['close'] = df['c'].astype('float')*btcusd
      df['open'] = df['o'].astype('float')*btcusd
      df['high'] = df['h'].astype('float')*btcusd
      df['low'] = df['l'].astype('float')*btcusd

      self.DATAFRAME = df
      return df

  def rollstats_MACD(self):
    '''rolling statistics (also known as "financial indicators")
    ---MOVING AVERAGES STRATEGY (MACD)---'''
    df = self.DATAFRAME
    MA1 = 12
    MA2 = 26

    df['fast MA'] = df['close'].rolling(window=MA1).mean()
    df['slow MA'] = df['close'].rolling(window=MA2).mean()

    df['rollstats'] = df['fast MA'] - df['slow MA']

  def regimes(self):
    '''trading regimes'''
    df = self.DATAFRAME

    rollstats = df['rollstats']

    crossover = 0 

    df['regime'] = np.where(rollstats > crossover,1,0)
    df['regime'] = np.where(rollstats < -crossover,-1,df['regime'])

    df['signal'] = df['regime'].diff(periods=1) #signal rolling difference
    df['regime_old'] = df['regime']


  def strat_compute(self):
    '''COMPUTE STRATEGY -- MARKET V STRAT RESULTS '''
    df = self.DATAFRAME

    df['market'] = np.log(df['close'] / df['close'].shift(1))

    df['strategy'] =  df['regime'].shift(1) * df['market']

    df[['market','strategy']]=df[['market','strategy']].cumsum().apply(np.exp) 

    strategy_gain = df['strategy'].iloc[-1] - df['market'].iloc[-1]

    print('final return-on-investment: {:.2f}%'.format(strategy_gain*100) )

    df["signal"][df["signal"] == 0.0] = np.nan


