Getting Started
===============

Installation
--------------

Cointables can be installed using pip:

.. code-block:: bash

   pip install cointables

It is recommended you run Cointables using a `virtualenv` virtual environment. To do so, follow the below simple protocol to create the virtual environment, run it, and install the package there:

.. code-block:: bash

   virtualenv venv
   source venv/bin/activate
   pip install cointables

To exit the virtual environment, simply type ``deactivate``. To access it at any other time again, enter with the above source ``venv...`` command.

Easy GET
------------

Once you have installed Cointables, you can start using it to extract historical Open-High-Low-Close (OHLC) data for various cryptocurrencies from Binance.

You can use Cointables to extract OHLC data for Bitcoin (BTC) in USDT using 30-minute candles:

.. code-block:: python

   from cointables import Chart
   from binance.client import Client

   client = Client(api_key='my_api_key', api_secret='my_api_secret')
   btc_chart = Chart(client, coin='BTC', market='USDT', candles='30m')
   btc_chart.coinGET()
   print(btc_chart.dataframe)

>>> [/O]
                             open_time  ...           low
2023-04-06 02:59:59.999  1680766200000  ...  7.789329e+08
2023-04-06 03:29:59.999  1680768000000  ...  7.773495e+08
2023-04-06 03:59:59.999  1680769800000  ...  7.802205e+08
2023-04-06 04:29:59.999  1680771600000  ...  7.826171e+08
2023-04-06 04:59:59.999  1680773400000  ...  7.785227e+08
...                                ...  ...           ...
2023-04-16 10:29:59.999  1681657200000  ...  9.191869e+08
2023-04-16 10:59:59.999  1681659000000  ...  9.199183e+08
2023-04-16 11:29:59.999  1681660800000  ...  9.169926e+08
2023-04-16 11:59:59.999  1681662600000  ...  9.179277e+08
2023-04-16 12:29:59.999  1681664400000  ...  9.195774e+08

[500 rows x 16 columns]


This creates a `Chart` object with the specified parameters, calling the internal `get_data()` method to extract the OHLC data. The resulting data is returned as a Pandas DataFrame object, which can be used for further analysis and visualization.

For more detailed usage instructions, see the `cointables` package documentation.


