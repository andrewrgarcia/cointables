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

