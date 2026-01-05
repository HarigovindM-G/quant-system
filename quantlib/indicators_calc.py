# we can use tallib for technical indicators 
import talib
import numpy as np


def adx_series(high, low, close, n):
    return talib.ADX(high, low, close, timeperiod=n)


def ema_series(series, n):
    return talib.EMA(series, timeperiod=n)


def sma_series(series, n):
    return talib.SMA(series, timeperiod=n)
