from datetime import datetime, timedelta

import pandas as pd
import requests
import typing
from misc.constants import CRYPTO_DD_BASE_URL, COINGECKO_BASE_URL
from misc.utils import fetch_csv_as_dataframe


def get_provider(provider):
    """Get a registered provider

    Args:
        provider (str): binance, crypto_dd

    Returns: (function): our provider func with args 
    """
    providers = {
        "crypto_dd": _crypto_dd
    }

    return providers.get(provider, None)


def _crypto_dd(symbol="BTCUSDT", timeframe="d"):
    """
    Fetch data to the ohlcv format. (binance)

    Example :
    'timestamp', 'open', 'high', 'low', 'close', 'volume'
    2024-12-21 00:00:00,97805.44000,99540.61000,96398.39000,97291.99000,23483.54143
    2024-12-20 00:00:00,97461.86000,98233.00000,92232.54000,97805.44000,62884.13570

    Args:
        timeframe (str, optional): . Defaults to None.
        symbol (str, optional): . Defaults to "BTCUSDT".

    Returns:
       (pd.DataFrame): df
    """

    url = f"{CRYPTO_DD_BASE_URL}Binance_{symbol}_{timeframe}.csv"
    new_columns = [
        "timestamp", "date", "symbol", "open", "high",
        "low", "close", "volume", "volume_btc", "trade_count"
    ]
    df = fetch_csv_as_dataframe(url, new_columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.sort_values(by="timestamp")
    return df


def load_data(df, timeframe='D'):
    """
    Loads the CSV file from CryptoDataDownload format,
    sorts by date ascending, and optionally resamples
    to weekly ('W') or monthly ('M') data.

    :param (pd.DataFrame) df: path to CSV
    :param timeframe: 'D' for daily, 'W' for weekly, 'M' for monthly
    :return (pd.DataFrame): a pandas DataFrame
    """
    # Read data

    if timeframe == "4h":
        # Perform 4-hour resampling

        df = df.sort_values('timestamp')

        df.rename(columns={
            'timestamp': 'Date',
            'symbol': 'Symbol',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        df.set_index('Date', inplace=True)
        df = df.drop("date", axis=1)
        df = df.resample(timeframe).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })

        return df

    # Standardize column names
    df.rename(columns={
        'timestamp': 'Date',
        'symbol': 'Symbol',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)

    df = df.drop("date", axis=1)
    df = df.drop("volume_btc", axis=1)
    df = df.drop("trade_count", axis=1)
    df = df.drop("Symbol", axis=1)
    df.set_index('Date', inplace=True)

    if timeframe in ['W', 'M']:
        # Resample to the chosen timeframe
        # For OHLC data, we typically do:
        df = df.resample(timeframe).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
    else:
        # Otherwise, keep daily
        pass

    return df
