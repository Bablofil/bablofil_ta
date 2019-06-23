import math

# Simple moving average
# https://en.wikipedia.org/wiki/Moving_average
def SMA(data, period):
    if len(data) == 0:
        raise Exception("Empty data")
    if period <= 0:
        raise Exception("Invalid period")

    interm = 0
    result = []
    nan_inp = 0
    
    for i, v in enumerate(data):
        if math.isnan(data[i]):
            result.append(math.nan)
            interm = 0
            nan_inp += 1
        else:
            interm += v
            if (i+1 - nan_inp) < period:
                result.append(math.nan)
            else:
                result.append(interm/float(period))
                if not math.isnan(data[i+1-period]):
                    interm -= data[i+1-period]
    return result

# Calculates various EMA with different smoothing multipliers, see lower
def generalEMA(data, period, multiplier):
    if period <= 1:
        raise Exception("Invalid period")

    sma = SMA(data, period)
    
    result = []
    for k, v in enumerate(sma):
        if math.isnan(v):
            result.append(math.nan)
        else:
            prev = result[k-1]
            if math.isnan(prev):
                result.append(v)
                continue
            ema = (data[k]-prev)*multiplier + prev
            result.append(ema)
    return result

# Exponential moving average
# https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
def EMA(data, period):
    return generalEMA(data, period, 2/(float(period)+1.0))

# Synonym to EMA
def EWMA(data, period):
    return EMA(data, period)

# Modified moving average
# https://en.wikipedia.org/wiki/Moving_average
def SMMA(data, period):
    return generalEMA(data, period, 1/(float(period)))

# Synonym to SMMA
def RMA(data, period):
    return SMMA(data, period)
# Synonym to SMMA
def MMA(data, period):
    return SMMA(data, period)

# Double exponential moving average
# https://en.wikipedia.org/wiki/Double_exponential_moving_average
def D2(data, period):
    ema = EMA(data, period)
    ema_ema = EMA(ema, period)
    e2 = list(map(lambda x: x*2, ema))
    
    result = []
    
    for i in range(len(data)):
        result.append(e2[i] - ema_ema[i])
    return result

# Double exponential moving average
def DEMA(data, period):
    return D2(data, period)

# Double exponential moving average
def DMA(data, period):
    return D2(data, period)

# Triple Exponential Moving Average
# https://en.wikipedia.org/wiki/Triple_exponential_moving_average
def T3(data, period):
    e1 = EMA(data, period)
    e2 = EMA(e1, period)
    e3 = EMA(e2, period)

    e1 = list(map(lambda x: x*3, e1))
    e2 = list(map(lambda x: x*3, e2))

    result = []
    for i in range(len(data)):
        result.append(e1[i] - e2[i] + e3[i])
        
    return result

# Triple Exponential Moving Average
def TEMA(data, period):
    return T3(data, period)

# Triple Exponential Moving Average
def TMA(data, period):
    return T3(data, period)

# Moving average convergence/divergence
# https://en.wikipedia.org/wiki/MACD
def MACD(data, fastperiod, slowperiod, signalperiod):
    macd, macdsignal, macdhist = [], [], []

    fast_ema = EMA(data, fastperiod)
    slow_ema = EMA(data, slowperiod)
    
    diff = []

    for k, fast in enumerate(fast_ema):
        if math.isnan(fast) or math.isnan(slow_ema[k]):
            macd.append(math.nan)
            macdsignal.append(math.nan)
        else:
            macd.append(fast-slow_ema[k])
            diff.append(macd[k])

    diff_ema = EMA(diff, signalperiod)
    macdsignal = macdsignal + diff_ema

    for k, ms in enumerate(macdsignal):
        if math.isnan(ms) or math.isnan(macd[k]):
            macdhist.append(math.nan)
        else:
            macdhist.append(macd[k] - macdsignal[k])

    return macd, macdsignal, macdhist

# Relative strength index
# https://en.wikipedia.org/wiki/Relative_strength_index
def RSI(data, period):
    u_days = []
    d_days = []

    for i, _ in enumerate(data):
        if i == 0:
            u_days.append(0)
            d_days.append(0)
        else:
            if data[i] > data[i-1] :
                u_days.append(data[i] - data[i-1])
                d_days.append(0)
            elif data[i] < data[i-1]:
                d_days.append(data[i-1] - data[i])
                u_days.append(0)
            else:
                u_days.append(0)
                d_days.append(0)

    smma_u = SMMA(u_days, period)
    smma_d = SMMA(d_days, period)

    result = []

    for k, _ in enumerate(data):
        if smma_d[k] == 0:
            result.append(100)
        else:
            result.append(100 - (100 / (1 + smma_u[k]/smma_d[k])))

    return result

# Stochastic oscillator
# https://en.wikipedia.org/wiki/Stochastic_oscillator
def STOCH(high, low, closes, fastk_period, slowk_period, slowd_period):
    fastk = []
    
    for i, _ in enumerate(closes):
        if (i + 1) < fastk_period:
            fastk.append(math.nan)
        else:
            lower_bound = i + 1 - fastk_period
            upper_bound = i + 1
            curr_low = min(low[lower_bound:upper_bound])
            curr_high = max(high[lower_bound:upper_bound])
            fastk.append(((closes[i] - curr_low) / (curr_high - curr_low)) * 100)
       
    fastk = EMA(fastk, slowk_period)
    slowd = EMA(fastk, slowd_period)

    return fastk, slowd

# RSI + STOCH
# https://www.investopedia.com/terms/s/stochrsi.asp
def STOCHRSI(data, period, fastk_period, fastd_period):
    rsi = RSI(data, period)
    return STOCH(rsi, rsi, rsi, period, fastk_period, fastd_period)
    
# Bollinger Bands
# https://en.wikipedia.org/wiki/Bollinger_Bands
def BBANDS(data, ma=SMA, ma_period=20, dev_val=2):
    middle = ma(data, ma_period)

    # calculating stddev. We won't count NaN values. Also NaNs are reasons not to use statistics.stddev, numpy, etc.
    stddevs = []
    real_data_cnt = 0
    
    for i in range(len(data)):
        if math.isnan(middle[i]):
            stddevs.append(0)
            real_data_cnt += 1
            continue

        if i-real_data_cnt >= ma_period:
            avg = sum(middle[i-ma_period+1:i+1])/ma_period
            s = sum(map(lambda x: math.pow(x - avg,2), middle[i-ma_period+1:i+1]))
            stddev_avg = s/ma_period
            stddev = math.sqrt(stddev_avg)
            stddevs.append(stddev)
        else:
           stddevs.append(0) 

    upper = []
    lower = []
    for i in range(len(middle)):
        if not math.isnan(middle[i]):
            upper.append(middle[i]+stddevs[i]*dev_val)
            lower.append(middle[i]-stddevs[i]*dev_val)
        else:
            upper.append(math.nan)
            lower.append(math.nan)
    return upper, middle, lower
    

