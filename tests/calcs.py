import numpy as np

def rollstats_MACD(df):
    """Compute the rolling statistics (also known as "financial indicators") using the Moving Averages Strategy (MACD) """
    MA1 = 12
    MA2 = 26

    df['fast MA'] = df['close'].rolling(window=MA1).mean()
    df['slow MA'] = df['close'].rolling(window=MA2).mean()

    df['rollstats'] = df['fast MA'] - df['slow MA']

    return df

def regimes(df):
    """Assign trading regimes to the data based on the computed rolling statistics."""

    rollstats = df['rollstats']

    crossover = 0

    df['regime'] = np.where(rollstats > crossover, 1, 0)
    df['regime'] = np.where(rollstats < -crossover, -1, df['regime'])

    df['signal'] = df['regime'].diff(
        periods=1)  # signal rolling difference
    df['regime_old'] = df['regime']

    return df

def strat_compute(df):
    """
    Compute the market and strategy returns based on the assigned trading regimes,
    and print the final return-on-investment as a message.

    The computed signal is used to fill the gaps in the signal of the trading regime.
    """

    df['market'] = np.log(df['close'] / df['close'].shift(1))

    df['strategy'] = df['regime'].shift(1) * df['market']

    df[['market', 'strategy']] = df[[
        'market', 'strategy']].cumsum().apply(np.exp)

    strategy_gain = df['strategy'].iloc[-1] - df['market'].iloc[-1]

    message = 'final return-on-investment: {:.2f}%'.format(
        strategy_gain*100)

    print(message)

    df["signal"][df["signal"] == 0.0] = np.nan

    return df
