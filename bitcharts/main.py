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


def coinpair(quote, interval = '1d',base='USDT'):
    '''returns ohlc data of the quote cryptocurrency with
     the base currency (i.e. 'market'); base for alts must be either USDT or BTC'''

    btcusd = 1 if quote == 'BTC' else \
    get_bars('BTCUSDT', interval = interval)['c'].astype('float') \
    if base == 'USDT' else 1

    base0 = 'USDT' if quote == 'BTC' else 'BTC'

    df = get_bars(quote + base0, interval = interval)

    df['close'] = df['c'].astype('float')*btcusd
    df['open'] = df['o'].astype('float')*btcusd
    df['high'] = df['h'].astype('float')*btcusd
    df['low'] = df['l'].astype('float')*btcusd

    return df

def get_bars(quote, interval = INTERVAL):

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

  return df


def rollstats(df):
  '''rolling statistics (also known as "financial indicators")'''
  '---MOVING AVERAGES STRATEGY (MACD)---'
  MA1 = 12
  MA2 = 26

  df['fast MA'] = df['close'].rolling(window=MA1).mean()
  df['slow MA'] = df['close'].rolling(window=MA2).mean()

  df['MACD'] = df['fast MA'] - df['slow MA']

def regimes(df):
  '''trading regimes'''

  MACD = df['MACD']

  crossover = 0 

  df['regime'] = np.where(MACD > crossover,1,0)
  df['regime'] = np.where(MACD < -crossover,-1,df['regime'])

  df['signal'] = df['regime'].diff(periods=1) #signal rolling difference
  df['regime_old'] = df['regime']


def martingale(df):
  'init variables'
  memo = 1          #multiplies the regime col
  close_up, close_dn = 0,0
  PROFIT_SELL = 1
  MART_RESET = 0
  for i in range(df['regime'].shape[0]):

    if df['signal'][i] < 0:
      'sell'
      close_dn = df['close'][i]

      if memo < 1:
        memo *=-1
      
      PROFIT_SELL = close_dn - close_up

      if PROFIT_SELL < 0:
        memo *= -2
        MART_RESET = 0
      
      if PROFIT_SELL >= 0:
        memo = 1
        MART_RESET = 1


    if df['signal'][i] > 0:
      'buy'
      close_up = df['close'][i]

      if memo < 1:
        memo *=-1

      if MART_RESET:
        memo = 1
        MART_RESET = 0 

      'non-greedy [during sell] constraint'
      # PROFIT_BUY = -PROFIT_SELL
      # if PROFIT_BUY >= 0 and memo > 2:
      #   memo = -1


    df['regime'][i] *= memo




def strat_compute(df):
  '''COMPUTE STRATEGY -- MARKET V STRAT RESULTS '''

  df['market'] = np.log(df['close'] / df['close'].shift(1))

  df['strategy'] =  df['regime'].shift(1) * df['market']

  df[['market','strategy']]=df[['market','strategy']].cumsum().apply(np.exp) 

  strategy_gain = df['strategy'].iloc[-1] - df['market'].iloc[-1]

  print('final return-on-investment: {:.2f}%'.format(strategy_gain*100) )

  df["signal"][df["signal"] == 0.0] = np.nan






def backtest(df,mart=False):

  rollstats(df)
  regimes(df)

  martingale(df) if mart else None

  strat_compute(df)

  'PLOTTING'
  ap = [
        mpf.make_addplot(df['market'],panel=1,type='line',ylabel='strategy',secondary_y=False),
        mpf.make_addplot(df['strategy'],panel=1,type='line',secondary_y=False),
        mpf.make_addplot(df['signal'],panel=2,type='scatter',\
                         markersize=100,marker='v',ylabel='signal'),
        mpf.make_addplot(df['regime_old'],panel=2,type='line',ylabel='regime'),
        mpf.make_addplot(df['regime'],panel=2,type='line',ylabel='regime'),
  ]

  s  = mpf.make_mpf_style(base_mpf_style='nightclouds',figcolor='#222')

  mpf.plot(df, title=coin+market+" ({} candles)".format(candles),\
          mav=(12,26), type='candle',ylabel='Candle',addplot=ap,panel_ratios=(2,1),\
          figratio=(1,1),figscale=1.5,style=s)
  


import mplfinance as mpf

print(mpf.available_styles())


coin = 'BTC'
market = 'USDT'
candles = '30m'

df=coinpair(coin, interval = candles,base=market)


backtest(df, False)
backtest(df, True)