
import requests        
import json           
import pandas as pd    
import numpy as np     

import matplotlib.pyplot as plt 

import datetime as dt
import pandas as pd


class Chart:
    def __init__(self, client, coin='BTC', market='USDT', candles='30m'):
        '''Chart class. Handler for the creation of financial charts for cryptocurrencies and analysis thereof

        Parameters
        ----------
        client : <binance.client.Client object>
            Binance API client object with API key and secret set
        coin : str
            Ticker name of quote currency (default: 'BTC')
        market : str
            Ticker name of base currency (default: 'USDT')
        candles : str
            Time interval for candles (default: '30m')
            Valid intervals are: '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        DATAFRAME : <pandas.DataFrame object>
            Financial data of price activity loaded from above information
        message : str
            Any message from an external function to store on Chart class (for easy migration across modules)
        '''
        self.client = client        # client binance object API key api secre7
        self.coin = coin
        self.market = market
        self.candles = candles
        self.DATAFRAME = []
        self.message = ''


    def get_bars__old(self):
        '''
        This method is no longer used and has been discontinued. It cannot perform GET requests when a remote server (such as Jupyter notebook or GitHub Actions) is used.

        It was originally adapted from the following source:
        "How to Download Historical Price Data from Binance with Python" by marketstack.
        (https://steemit.com/python/@marketstack/how-to-download-historical-price-data-from-binance-with-python)
        '''
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

    def get_data(self, time_diff=2419200000, num_candles=500):
        """
        Retrieve historical market data from the Binance API and return it as a Pandas DataFrame object.

        Parameters
        ---------------------------
        time_diff : int, optional
            An integer representing the time difference in milliseconds between the current time and the starting time of the historical data to retrieve. The default value is 2419200 seconds, which is equivalent to 28 days.
        num_candles : int
            An integer representing the number of historical candles to retrieve. The default value is 500. If this parameter is provided, it takes priority over the `time_diff` parameter.

        """
        current_time = int(dt.datetime.now().timestamp() * 1000)  # current time in milliseconds

        quote = self.coin + self.market
        interval = self.candles

        if num_candles is not None:
            candlesticks = self.client.get_historical_klines(
                quote, interval,
                limit=num_candles
            )
        else:
            candlesticks = self.client.get_historical_klines(
                quote, interval,
                str(current_time - time_diff),
                str(current_time)
            )

        df = pd.DataFrame(candlesticks)
        df.columns = ['open_time', 'o', 'h', 'l', 'c', 'v', 'close_time', 'qav', 'num_trades',
                      'taker_base_vol', 'taker_quote_vol', 'ignore']
        df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]

        self.DATAFRAME = df

        return df

    def coinGET(self,time_diff=2419200000, num_candles=500):
        '''Returns OHLC data of the quote cryptocurrency with the base currency (i.e., 'market').
        
        Note: The base currency for alts must be either USDT or BTC.
        
        Parameters
        -------------------
        time_diff : int, optional
            An integer representing the time difference in seconds between the current time and the starting time of the historical data to retrieve. The default value is 2419200 seconds, which is equivalent to 28 days.
        num_candles : int, optional
            An integer representing the number of historical candles to retrieve. The default value is 500. If this parameter is provided, it takes priority over the `time_diff` parameter.

        '''
        quote = self.coin
        base = self.market


        if quote == 'BTC':
            btcusd = 1
        elif base == 'USDT':
            self.coin = 'BTC'
            self.market = 'USDT'
            btcusd = self.get_data(time_diff, num_candles)['c'].astype('float')
        else:
            btcusd = 1

        self.market = 'USDT' if quote == 'BTC' else 'BTC'
        self.coin = quote

        df = self.get_data(time_diff, num_candles)

        df['close'] = df['c'].astype('float')*btcusd
        df['open'] = df['o'].astype('float')*btcusd
        df['high'] = df['h'].astype('float')*btcusd
        df['low'] = df['l'].astype('float')*btcusd

        self.DATAFRAME = df
        return df

    def rollstats_MACD(self):
        '''Compute the rolling statistics (also known as "financial indicators") using the Moving Averages Strategy (MACD) '''
        df = self.DATAFRAME
        MA1 = 12
        MA2 = 26

        df['fast MA'] = df['close'].rolling(window=MA1).mean()
        df['slow MA'] = df['close'].rolling(window=MA2).mean()

        df['rollstats'] = df['fast MA'] - df['slow MA']

    def regimes(self):
        '''Assign trading regimes to the data based on the computed rolling statistics.'''
        df = self.DATAFRAME

        rollstats = df['rollstats']

        crossover = 0

        df['regime'] = np.where(rollstats > crossover, 1, 0)
        df['regime'] = np.where(rollstats < -crossover, -1, df['regime'])

        df['signal'] = df['regime'].diff(
            periods=1)  # signal rolling difference
        df['regime_old'] = df['regime']

    def strat_compute(self):
        '''Compute the market and strategy returns based on the assigned trading regimes,
        and print the final return-on-investment as a message.

        The computed signal is used to fill the gaps in the signal of the trading regime.
        '''
        df = self.DATAFRAME

        df['market'] = np.log(df['close'] / df['close'].shift(1))

        df['strategy'] = df['regime'].shift(1) * df['market']

        df[['market', 'strategy']] = df[[
            'market', 'strategy']].cumsum().apply(np.exp)

        strategy_gain = df['strategy'].iloc[-1] - df['market'].iloc[-1]

        self.message = 'final return-on-investment: {:.2f}%'.format(
            strategy_gain*100)

        print(self.message)

        df["signal"][df["signal"] == 0.0] = np.nan
