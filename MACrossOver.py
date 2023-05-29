import pandas as pd
import numpy as np

def calculate_atr(data, n):
    high = data['High']
    low = data['Low']
    close = data['Close']
    tr = np.maximum(high - low, np.abs(high - close.shift(1)), np.abs(low - close.shift(1)))
    atr = tr.rolling(n).mean()
    data['ATR'] = atr
    return data

def calculate_ckstop(data, p, x, q):
    ihs = data['High'].rolling(p).max() - x * data['ATR']
    ils = data['Low'].rolling(p).min() + x * data['ATR']
    data['IHS'] = ihs
    data['ILS'] = ils
    data['CKS_short'] = ihs.rolling(q).max()
    data['CKS_long'] = ils.rolling(q).min()
    return data

# Load historical price data
data = pd.read_csv('historical_data.csv')  # Replace 'historical_data.csv' with your own dataset or API call

# Define moving average parameters
ma_fast_period = 9
ma_slow_period = 21
cks_p = 9
cks_x = 1
cks_q = 9

# Calculate moving averages
data['MA_fast'] = data['Close'].rolling(window=ma_fast_period).mean()
data['MA_slow'] = data['Close'].rolling(window=ma_slow_period).mean()

# Calculate ATR
data = calculate_atr(data, cks_p)

# Calculate Chande Kroll Stop (CKS) indicator
data = calculate_ckstop(data, cks_p, cks_x, cks_q)

# Initialize strategy parameters
position = 0  # Current position: 1 for long, -1 for short, 0 for no position
cash = 100000  # Available cash for trading
shares = 0  # Number of shares held
trades = []  # List to store trade details

# Implement MA crossover strategy with CKS stop loss
for i in range(1, len(data)):
    current_price = data['Close'][i]
    prev_price = data['Close'][i - 1]
    ma_fast = data['MA_fast'][i]
    ma_slow = data['MA_slow'][i]
    prev_ma_fast = data['MA_fast'][i - 1]
    prev_ma_slow = data['MA_slow'][i - 1]
    cks_long = data['CKS_long'][i]
    cks_short = data['CKS_short'][i]

    # Check for long entry signal
    if prev_ma_fast <= prev_ma_slow and ma_fast > ma_slow and position == 0:
        shares = cash / current_price
        cash = 0
        position = 1
        trades.append(('Buy', current_price))
    # Check for short entry signal
    elif prev_ma_fast >= prev_ma_slow and ma_fast < ma_slow and position == 0:
        shares = -cash / current_price  # Short position
        cash = 0
        position = -1
        trades.append(('Short', current_price))
    # Check for exit signal (stop loss)
    elif position != 0 and ((position == 1 and current_price < prev_price - cks_long) or (position == -1 and current_price > prev_price + cks_short)):
        cash = shares * current_price
        shares = 0
        position = 0
        trades.append(('Sell', current_price))

# Calculate final portfolio value
portfolio_value = cash if position == 0 else shares * data['Close'].iloc[-1]

# Print trade details and final portfolio value
print('Trade Details:')
for trade in trades:
    print(f'{trade[0]} at {trade[1]}')
print(f'\nFinal Portfolio Value: ${portfolio_value:.2f}')
