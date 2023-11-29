
"""
As a financial quantitative analyst, to compute leading indicators using ETF prices for TLT (iShares 20+ Year Treasury Bond ETF) and IEF (iShares 7-10 Year Treasury Bond ETF), you will need to create features that capture trends, momentum, volatility, and possibly mean reversion. These features can be derived from the price, Net Asset Value (NAV), and volume data.

We'll assume your data is structured in a pandas DataFrame with columns representing the different types of data for each ETF. Below is a Python code using pandas to calculate various features:

Simple Moving Averages (SMA): Calculate short-term and long-term moving averages.
Exponential Moving Averages (EMA): More weight to recent prices.
Relative Strength Index (RSI): Momentum indicator.
Bollinger Bands: Measures market volatility.
Volume-Weighted Average Price (VWAP): An average price weighted by volume.
Price Rate of Change (ROC): Measures the percentage change in price.
"""

import pandas as pd
import numpy as np

# Assuming df is your DataFrame with columns
# ['Date', 'Ticker', 'Price_Bid', 'Price_Ask', 'NAV_Bid', 'NAV_Ask', 'Volume']

# Set the Date as the index
df.set_index('Date', inplace=True)

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Function to calculate VWAP
def calculate_vwap(group):
    vwap = (group['Volume'] * group['Mid_Price']).cumsum() / group['Volume'].cumsum()
    return vwap

# Function to calculate indicators for each group
def calculate_indicators(group):
    # Calculate Mid Prices for Price
    group['Mid_Price'] = (group['Price_Bid'] + group['Price_Ask']) / 2

    # Calculate Simple Moving Averages
    group['SMA10'] = group['Mid_Price'].rolling(window=10).mean()
    group['SMA30'] = group['Mid_Price'].rolling(window=30).mean()

    # Calculate Exponential Moving Averages
    group['EMA12'] = group['Mid_Price'].ewm(span=12, adjust=False).mean()
    group['EMA26'] = group['Mid_Price'].ewm(span=26, adjust=False).mean()

    # Calculate Relative Strength Index (RSI)
    group['RSI'] = calculate_rsi(group['Mid_Price'])

    # Calculate Bollinger Bands
    group['BBand_High'] = group['SMA30'] + (2 * group['Mid_Price'].rolling(window=30).std())
    group['BBand_Low'] = group['SMA30'] - (2 * group['Mid_Price'].rolling(window=30).std())

    # Calculate VWAP
    group['VWAP'] = calculate_vwap(group)

    # Calculate Price Rate of Change
    group['ROC'] = group['Mid_Price'].pct_change(periods=10) * 100

    return group

# Apply the function to each Ticker group
df = df.groupby('Ticker').apply(calculate_indicators)

# Now df contains the original data along with the new features for each Ticker

# Function to calculate additional features related to NAV and Price dislocation
def calculate_nav_price_features(group):
    # Calculate the spread and percentage spread between NAV and Price
    group['NAV_Price_Spread'] = group['Mid_NAV'] - group['Mid_Price']
    group['NAV_Price_Spread_Percent'] = (group['NAV_Price_Spread'] / group['Mid_Price']) * 100

    # Calculate a moving average of the spread
    group['NAV_Price_Spread_MA10'] = group['NAV_Price_Spread'].rolling(window=10).mean()

    return group

# Function to generate trading signals and signal strength
def generate_trading_signals(group):
    # Define thresholds for signal generation
    spread_threshold = 0.5  # example threshold, needs to be optimized
    strength_threshold = 0.2  # example threshold for signal strength

    # Generate signals based on the spread
    group['Trade_Signal'] = np.where(group['NAV_Price_Spread_Percent'] > spread_threshold, 'Buy', 
                                     np.where(group['NAV_Price_Spread_Percent'] < -spread_threshold, 'Sell', 'Hold'))

    # Calculate signal strength based on the magnitude of the spread percentage
    group['Signal_Strength'] = np.abs(group['NAV_Price_Spread_Percent']) / strength_threshold

    return group

# Apply the functions to each Ticker group
df = df.groupby('Ticker').apply(calculate_nav_price_features)
df = df.groupby('Ticker').apply(generate_trading_signals)

# Now df contains the original data, additional features, and trading signals
