import cointables as coin 
import mplfinance as mpf

from binance.client import Client
import tests.config as config
import tests.calcs as calcs


def test_backtest(title_extra='MACD'):
    """
    Backtests MACD signal against the market for a specific cryptocurrency.

    This function uses the cointables package to retrieve cryptocurrency price data from Binance and then performs a
    backtest of the MACD signal against the market. It then plots the resulting data using the mplfinance package.

    Note: This function is for educational purposes only and is not intended to be used for financial advice.

    Parameters
    -------------
    title_extra : str, optional
        An optional title to add to the plot.

    """

    # Create a new instance of the Chart class with the specified client, coin, market, and candle settings
    chart = coin.Chart(client=Client(config.API_KEY, config.API_SECRET))
    chart.coin = 'ETH'
    chart.market = 'USDT'
    chart.candles = '1w'

    # Retrieve price data from Binance using the Chart class
    chart.coinGET()
    print(chart.dataframe)

    # Perform MACD calculations and strategy computations
    df = calcs.rollstats_MACD(chart.dataframe)
    df = calcs.regimes(df)
    df = calcs.strat_compute(df)

    # Define addplots for the mplfinance plot
    ap = [
        mpf.make_addplot(df['market'], panel=1, type='line', ylabel='strategy', secondary_y=False),
        mpf.make_addplot(df['strategy'], panel=1, type='line', secondary_y=False),
        mpf.make_addplot(df['signal'], panel=2, type='scatter', markersize=100, marker='v', ylabel='signal'),
        mpf.make_addplot(df['regime_old'], panel=2, type='line', ylabel='regime'),
        mpf.make_addplot(df['regime'], panel=2, type='line', ylabel='regime'),
    ]

    # Define the style for the mplfinance plot
    s = mpf.make_mpf_style(base_mpf_style='nightclouds', figcolor='#222')

    # Plot the data using mplfinance
    mpf.plot(df, title=chart.coin + chart.market + " ({} candles) {}".format(chart.candles, title_extra),\
             mav=(12, 26), type='candle', ylabel='Candle', addplot=ap, panel_ratios=(2, 1), xlabel=chart.message,\
             figratio=(1, 1), figscale=1.5, style=s)


# backtest('MACD')
