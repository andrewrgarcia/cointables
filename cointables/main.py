import pandas as pd    
import numpy as np     
import datetime as dt

class Chart:
    def __init__(self, client, coin='BTC', market='USDT', candles='30m'):
        """
        Chart class. Handler for the creation of financial charts for cryptocurrencies and analysis thereof

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

        Attributes
        ----------------
        dataframe : <pandas.DataFrame object>
            A DataFrame object containing the financial data of price activity loaded from above information.
        message : str
            Any message from an external function to store on Chart class (for easy migration across modules).
        sampled_epoch : int or None
            The epoch timestamp (either randomly sampled or set by user) see: `get_data_random` method. 
        """
        self.client = client        # client binance object API key api secret
        self.coin = coin
        self.market = market
        self.candles = candles
        self.dataframe = pd.DataFrame()
        self.message = ''
        self.sampled_epoch = None

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

        self.dataframe = df

        return df
    

    def _get_candle_width(self):
        """Returns the candle width (in milliseconds) for the specified interval."""
        intervals = {
            'm': 60 * 1000,
            'h': 3600 * 1000,
            'd': 86400 * 1000,
            'w': 604800 * 1000,
            'M': 2592000 * 1000,
        }
        if self.candles[-1] not in intervals:
            raise ValueError(f'Invalid interval: {self.candles}')
        
        return int(self.candles[:-1]) * intervals[self.candles[-1]]



    def get_data_random(self, sampled_time=None, num_candles=500, time_diff=2419200000):
        """
        Fetches historical market data for a randomly sampled epoch timestamp or a specified timestamp within the range of 
        Thursday, July 13, 2017 8:26:40 AM GMT (1500000000) and Friday, September 9, 2022 8:54:54 AM GMT (1665308894), with a 
        chart time frame defined by the time difference between the sampled epoch timestamp and the end time.

        Parameters:
        -----------
        sampled_time : float, optional
            The epoch timestamp to use as the starting point for fetching data. If None, a random timestamp is sampled from 
            the range between 1500000000 and 1665308894. Default is None.
                
        num_candles : int, optional
            The number of candles to sample for the specified or randomly sampled epoch timestamp. If None, the full time frame 
            using the given time_diff value will be used. Default is 500. NOTE: This parameter takes priority over `time_diff`
        
        time_diff : int, optional
            The size of the chart time frame between the specified or randomly sampled epoch timestamp and the end time, in 
            milliseconds. Default is 2419200000 (28 days). NOTE: `num_candles` must be set to None to activate this parameter. 

        Returns:
        --------
        pandas.DataFrame
            A dataframe containing the OHLCV data for the specified or randomly sampled epoch timestamp.
        """
        if sampled_time is not None:
            self.sampled_epoch = sampled_time
        else:
            self.sampled_epoch = np.random.uniform(1500000000, 1665308894)

        quote = self.coin + self.market
        interval = self.candles

        if num_candles is None:
            start_time = self.sampled_epoch - (time_diff // 1000)
            end_time = self.sampled_epoch
            candlesticks = self.client.get_historical_klines(
                quote, interval, str(start_time * 1000), str(end_time * 1000)
            )
            
        else:
            end_time = self.sampled_epoch
            interval_seconds = self._get_candle_width()
            start_time = end_time - dt.timedelta(seconds=(interval_seconds // 1000) * num_candles).total_seconds()

            candlesticks = self.client.get_historical_klines(
                quote, interval, str(start_time * 1000), str(end_time * 1000),limit=num_candles
            )

        df = pd.DataFrame(candlesticks, columns=['open_time', 'o', 'h', 'l', 'c', 'v', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
        df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]

        self.dataframe = df

        return df
        

    def coinGET_custom(self,GET_METHOD):
        """        
        Returns OHLC data of the quote cryptocurrency with the base currency (i.e., `market`) for a custom GET_METHOD. Note: The base currency for alts must be either USDT or BTC.
        
        Parameters
        -------------
        GET_METHOD : function
            A custom GET_METHOD that returns the OHLC data for a specific cryptocurrency market.

        Example
        -----------
        >>> def get_btc_data():
        >>>     # Some code that fetches and returns OHLC data for the BTC/USDT market.
        >>>     return btc_data
        >>>
        >>> chart = Chart('BTC', 'USDT', '1d')
        >>> btc_df = chart.coinGET_custom(get_btc_data)
        """
        if self.market not in ['BTC', 'USDT']:
            raise ValueError('The base currency for altcoins must be either USDT or BTC.')

        # Get the current BTC/USDT exchange rate
        if self.market == 'USDT':
            btcusd = GET_METHOD['c'].astype('float')
        else:
            btcusd = 1

        # Get the OHLC data from the custom GET_METHOD and convert the prices to the base currency
        df = GET_METHOD
        df['close'] = df['c'].astype('float') * btcusd
        df['open'] = df['o'].astype('float') * btcusd
        df['high'] = df['h'].astype('float') * btcusd
        df['low'] = df['l'].astype('float') * btcusd

        # Set the base currency and cryptocurrency of the object to match the OHLC data
        if self.market == 'USDT':
            self.market = 'USDT'
            self.coin = self.coin
        else:
            self.market = 'BTC'
            self.coin = self.coin

        # Save the OHLC data as a dataframe and return it
        self.dataframe = df
        return df


    def coinGET(self,time_diff=2419200000, num_candles=500):
        """
        Returns OHLC data of the quote cryptocurrency with the base currency (i.e., 'market'). Note: The base currency for alts must be either USDT or BTC.
        
        Parameters
        -------------------
        time_diff : int, optional
            An integer representing the time difference in seconds between the current time and the starting time of the historical data to retrieve. The default value is 2419200 seconds, which is equivalent to 28 days.
        num_candles : int, optional
            An integer representing the number of historical candles to retrieve. The default value is 500. If this parameter is provided, it takes priority over the `time_diff` parameter.

        """
        df = self.coinGET_custom(self.get_data(time_diff, num_candles))

        return df

    def coinGET_random(self, sampled_time=None, num_candles=500, time_diff=2419200000):
        """
        Returns OHLC data of the quote cryptocurrency with the base currency (i.e., 'market') in a randomly chosen time window with a chart time frame defined by the time difference 
        between the sampled epoch timestamp and the end time, where the chart time frame is set to time_diff.

        Parameters
        ----------------
        sampled_time : float
            Uses the given epoch timestamp to fetch data. 
            The default value is np.random.uniform(1500000000, 1665308894). It samples a timestamp randomly between Thursday, July 13, 2017 8:26:40 AM GMT (1500000000) 
            and Friday, September 9, 2022 8:54:54 AM GMT (1665308894).
            
        num_candles : int, optional
            The number of candles to sample for the full time frame.
            Default: 500 candles (If None, samples the full time frame using the given time_diff value).

        time_diff : int, optional
            The size of the chart time frame between the specified or randomly sampled epoch timestamp and the end time, in milliseconds. 
            The default value is 28 days (2419200000 milliseconds). time_diff will activate if num_candles is set to None
        """
        df = self.coinGET_custom(self.get_data_random(
            sampled_time, num_candles, time_diff))

        return df
