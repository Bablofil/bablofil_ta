```
import requests
import bablofil_ta as ta

# get klines from binance (LTCBNB) and use their data for indicators
r = requests.get("https://api.binance.com/api/v1/klines?symbol=LTCBNB&interval=1d&limit=100").json()

closes = [float(x[4]) for x in r]
high = [float(x[2]) for x in r]
low = [float(x[3]) for x in r]
vol = [float(x[5]) for x in r]

print("SMA", ta.SMA(closes, 5))
print("EMA", ta.EMA(closes, 5))
print("SMMA", ta.SMMA(closes, 5))
print("DEMA", ta.DEMA(closes, 5))
print("TEMA", ta.TEMA(closes, 5))

macd, macdsignal, macdhist = ta.MACD(closes, 12, 26, 9)
print("MACD", macd)
print("MACD SIGNAL", macdsignal)
print("MACD HIST", macdhist)

print("RSI", ta.RSI(closes, 9))
print("STOCH",  ta.STOCH(high, low, closes, 5, 3, 3))
print("STOCHRSI", ta.STOCHRSI(closes, 14, 3, 3))

upper, middle, lower = ta.BBANDS(closes, ma_period=20, )
print("BBANDS UPPER",upper)
print("BBANDS MIDDLE",middle)
print("BBANDS LOWER",lower)


print(ta.MFI(high, low, close, vol, 14))
```
