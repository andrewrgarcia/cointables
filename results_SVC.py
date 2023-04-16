from sklearn.svm import SVC
import pandas as pd
import numpy as np

import bitcharts as bits
import mplfinance as mpf


def strat_compute_SVC(chart_obj):

  df = chart_obj.DATAFRAME
  '''COMPUTE STRATEGY -- MARKET V STRAT RESULTS '''
  data = pd.DataFrame(df['close'])
  data['market'] = np.log(data / data.shift())
  data.dropna(inplace=True)

  '''LAGGED SIGNS OF LOG RATES OF RETURN 
  credit: Yves Hilpisch. 2018. Python for Finance: Analyze Big Financial Data (2nd. ed.). O'Reilly Media, Inc. '''
  lags = 6
  cols = []
  for lag in range(1, lags + 1):
    col = 'lag_{}'.format(lag)
    data[col] = np.sign(data['market'].shift(lag))
    cols.append(col)
    data.dropna(inplace=True)

  model = SVC(gamma='auto')
  model.fit(data[cols], np.sign(data['market']))

  data['actual_sign'] = np.sign(data['market'])
  data['prediction'] = model.predict(data[cols])

  data['strategy'] = data['prediction'] * data['market']
  data[['market','strategy']]=data[['market','strategy']].cumsum().apply(np.exp) 

  strategy_gain = data['strategy'].iloc[-1] - data['market'].iloc[-1]

  chart_obj.message = 'final anticipated ROI: {:.2f}%'.format(strategy_gain*100)
  print(chart_obj.message )

  return data 


from binance.client import Client
import config

def backtest():
  
  chart = bits.Chart(client = Client(config.API_KEY, config.API_SECRET))

  chart.coin = "BTC"
  chart.market = "USDT"
  chart.candles = "30m"
  
  chart.coinGET(num_candles=None)
  
  df = chart.DATAFRAME

  data = strat_compute_SVC(chart)
  diff_rows = df['close'].shape[0] - data['strategy'].shape[0]

  'PLOTTING'
  ap = [
        mpf.make_addplot(data['market'],panel=1,type='line',ylabel='strategy',secondary_y=False),
        mpf.make_addplot(data['strategy'],panel=1,type='line',secondary_y=False),
        mpf.make_addplot(data['actual_sign'],panel=2,type='line',ylabel='prediction'),
        mpf.make_addplot(data['prediction'],panel=2,type='line',ylabel='prediction')
  ]

  s  = mpf.make_mpf_style(base_mpf_style='nightclouds',figcolor='#222')


  mpf.plot(df[diff_rows:], title=chart.coin+chart.market+"({} candles) -- Support Vector Machines".format(chart.candles),\
          mav=(12,26),type='candle',ylabel='Candle',addplot=ap,panel_ratios=(2,1),xlabel=chart.message,\
          figratio=(1,1),figscale=1.5,style=s)
  

backtest()