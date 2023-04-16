def martingale(df):
  '''
  Implements the martingale betting strategy for trading cryptocurrencies.

  Parameters
  -------------
  df : pandas.DataFrame
      A DataFrame containing the trading data, including the 'signal' and 'regime' columns.

  Notes
  ---------
  This function uses the martingale betting strategy to determine position sizing for buying and selling cryptocurrencies.
  When a sell signal is triggered, the position size is increased by a factor of two if the profit from the trade is negative. 
  When a buy signal is triggered, the position size is reset to 1 if the last trade was a profitable sell. If the last trade was not profitable, the position size remains the same. 

  The 'regime' column of the DataFrame is multiplied by the position size to determine the size of each trade.
  '''

  # init variables
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

