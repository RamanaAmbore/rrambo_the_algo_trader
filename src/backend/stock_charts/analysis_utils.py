# src/stock_charts/analysis_utils.py
from datetime import datetime
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd

from src.helpers.logger import get_logger

logger = get_logger(__name__)

def calculate_sma(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """
    Calculate Simple Moving Average for a DataFrame
    
    Args:
        df: DataFrame with price data
        period: Period for the moving average calculation
        column: Column name to use for calculation
        
    Returns:
        Series containing the SMA values
    """
    if df.empty or column not in df.columns:
        return pd.Series(dtype=float)
        
    return df[column].rolling(window=period).mean()

def calculate_ema(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """
    Calculate Exponential Moving Average for a DataFrame
    
    Args:
        df: DataFrame with price data
        period: Period for the moving average calculation
        column: Column name to use for calculation
        
    Returns:
        Series containing the EMA values
    """
    if df.empty or column not in df.columns:
        return pd.Series(dtype=float)
        
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """
    Calculate Relative Strength Index (RSI) for a DataFrame
    
    Args:
        df: DataFrame with price data
        period: Period for the RSI calculation
        column: Column name to use for calculation
        
    Returns:
        Series containing the RSI values
    """
    if df.empty or column not in df.columns or len(df) < period + 1:
        return pd.Series(dtype=float)
        
    # Calculate price changes
    delta = df[column].diff()
    
    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss.replace(0, 1e-10)  # Avoid division by zero
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, 
                  signal_period: int = 9, column: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Moving Average Convergence Divergence (MACD) for a DataFrame
    
    Args:
        df: DataFrame with price data
        fast_period: Period for the fast EMA
        slow_period: Period for the slow EMA
        signal_period: Period for the signal line EMA
        column: Column name to use for calculation
        
    Returns:
        Tuple of (MACD Line, Signal Line, Histogram)
    """
    if df.empty or column not in df.columns:
        empty_series = pd.Series(dtype=float)
        return empty_series, empty_series, empty_series
        
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(df, period=fast_period, column=column)
    slow_ema = calculate_ema(df, period=slow_period, column=column)
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0, 
                             column: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands for a DataFrame
    
    Args:
        df: DataFrame with price data
        period: Period for the moving average and standard deviation
        std_dev: Number of standard deviations for the bands
        column: Column name to use for calculation
        
    Returns:
        Tuple of (Middle Band, Upper Band, Lower Band)
    """
    if df.empty or column not in df.columns:
        empty_series = pd.Series(dtype=float)
        return empty_series, empty_series, empty_series
        
    # Calculate middle band (SMA)
    middle_band = calculate_sma(df, period=period, column=column)
    
    # Calculate standard deviation
    rolling_std = df[column].rolling(window=period).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)
    
    return middle_band, upper_band, lower_band

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR) for a DataFrame
    
    Args:
        df: DataFrame with price data (must have high, low, close columns)
        period: Period for the ATR calculation
        
    Returns:
        Series containing the ATR values
    """
    if df.empty or not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.Series(dtype=float)
        
    # Calculate True Range
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    # Get the maximum of the three ranges
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate ATR
    atr = true_range.rolling(window=period).mean()
    
    return atr

def detect_support_resistance(df: pd.DataFrame, window: int = 10, threshold: float = 0.05, column: str = 'close') -> Dict[str, List[float]]:
    """
    Detect support and resistance levels
    
    Args:
        df: DataFrame with price data
        window: Window size for local minima/maxima detection
        threshold: Threshold for grouping similar levels (as a percentage)
        column: Column name to use for calculation
        
    Returns:
        Dictionary with 'support' and 'resistance' levels
    """
    if df.empty or column not in df.columns or len(df) < window * 2:
        return {'support': [], 'resistance': []}
        
    price_series = df[column]
    
    # Identify local maxima and minima
    local_max = []
    local_min = []
    
    for i in range(window, len(price_series) - window):
        # Check if current price is a local maximum
        if price_series.iloc[i] == max(price_series.iloc[i-window:i+window+1]):
            local_max.append(price_series.iloc[i])
        # Check if current price is a local minimum
        if price_series.iloc[i] == min(price_series.iloc[i-window:i+window+1]):
            local_min.append(price_series.iloc[i])
    
    # Group similar levels
    def group_levels(levels: List[float], threshold: float) -> List[float]:
        if not levels:
            return []
            
        # Sort levels
        sorted_levels = sorted(levels)
        
        # Group similar levels
        grouped_levels = []
        current_group = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            # If level is close to the average of the current group
            if level <= current_group[-1] * (1 + threshold):
                current_group.append(level)
            else:
                # Add average of current group to the results
                grouped_levels.append(sum(current_group) / len(current_group))
                # Start a new group
                current_group = [level]
                
        # Add the last group
        if current_group:
            grouped_levels.append(sum(current_group) / len(current_group))
            
        return grouped_levels
    
    # Group similar support and resistance levels
    support_levels = group_levels(local_min, threshold)
    resistance_levels = group_levels(local_max, threshold)
    
    # Limit to recent relevance
    support_levels = support_levels[-5:] if len(support_levels) > 5 else support_levels
    resistance_levels = resistance_levels[-5:] if len(resistance_levels) > 5 else resistance_levels
    
    return {
        'support': support_levels,
        'resistance': resistance_levels
    }

def calculate_fibonacci_levels(df: pd.DataFrame, use_recent: bool = True) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement levels
    
    Args:
        df: DataFrame with price data (must have high and low columns)
        use_recent: Use the most recent swing high/low if True, otherwise use all-time high/low
        
    Returns:
        Dictionary with Fibonacci levels
    """
    if df.empty or not all(col in df.columns for col in ['high', 'low']):
        return {}
        
    # Determine high and low prices
    if use_recent:
        # Use most recent 30 days (or fewer if less data available)
        lookback = min(30, len(df))
        recent_df = df.iloc[-lookback:]
        high_price = recent_df['high'].max()
        low_price = recent_df['low'].min()
    else:
        # Use all-time high and low
        high_price = df['high'].max()
        low_price = df['low'].min()
    
    # Calculate price range
    price_range = high_price - low_price
    
    # Calculate Fibonacci levels
    fib_levels = {
        'level_0': low_price,                    # 0%
        'level_0.236': low_price + 0.236 * price_range,  # 23.6%
        'level_0.382': low_price + 0.382 * price_range,  # 38.2%
        'level_0.5': low_price + 0.5 * price_range,    # 50%
        'level_0.618': low_price + 0.618 * price_range,  # 61.8%
        'level_0.786': low_price + 0.786 * price_range,  # 78.6%
        'level_1': high_price                   # 100%
    }
    
    return fib_levels

def identify_patterns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Identify common chart patterns
    
    Args:
        df: DataFrame with price data (must have open, high, low, close columns)
        
    Returns:
        Dictionary with detected patterns and their locations
    """
    if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        return {'patterns': []}
        
    # This is a simplified version - pattern detection is complex
    patterns = []
    
    # Example: Detect potential doji candles (open and close are very close)
    recent_candles = df.iloc[-5:].copy()  # Look at the most recent 5 candles
    for i, row in recent_candles.iterrows():
        if abs(row['open'] - row['close']) < (row['high'] - row['low']) * 0.1:
            patterns.append(f"Doji candle on {i.strftime('%Y-%m-%d')}")
    
    # Example: Detect potential bullish engulfing
    for i in range(1, min(5, len(df) - 1)):
        prev = df.iloc[-i-1]
        curr = df.iloc[-i]
        
        # Bullish engulfing criteria
        if (prev['close'] < prev['open'] and  # Previous candle is bearish
            curr['open'] < prev['close'] and  # Current opens below previous close
            curr['close'] > prev['open'] and  # Current closes above previous open
            curr['close'] > curr['open']):    # Current candle is bullish
            
            patterns.append(f"Bullish engulfing on {df.index[-i].strftime('%Y-%m-%d')}")
    
    # Example: Look for potential head and shoulders (very simplified)
    if len(df) > 30:
        recent_df = df.iloc[-30:].copy()
        recent_df['peak'] = (recent_df['high'] > recent_df['high'].shift(1)) & (recent_df['high'] > recent_df['high'].shift(-1))
        peaks = recent_df[recent_df['peak']].copy()
        
        if len(peaks) >= 3:
            # Very simplified check - a real implementation would be more complex
            patterns.append("Potential head and shoulders pattern detected")
    
    return {'patterns': patterns}

def enhance_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enhance a DataFrame with common technical indicators
    
    Args:
        df: DataFrame with price data (must have open, high, low, close columns)
        
    Returns:
        Enhanced DataFrame with additional columns for technical indicators
    """
    if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        return df
        
    # Make a copy to avoid modifying the original
    enhanced_df = df.copy()
    
    # Add Simple Moving Averages
    enhanced_df['sma_20'] = calculate_sma(enhanced_df, period=20)
    enhanced_df['sma_50'] = calculate_sma(enhanced_df, period=50)
    enhanced_df['sma_200'] = calculate_sma(enhanced_df, period=200)
    
    # Add Exponential Moving Averages
    enhanced_df['ema_12'] = calculate_ema(enhanced_df, period=12)
    enhanced_df['ema_26'] = calculate_ema(enhanced_df, period=26)
    
    # Add RSI
    enhanced_df['rsi_14'] = calculate_rsi(enhanced_df, period=14)
    
    # Add MACD
    enhanced_df['macd_line'], enhanced_df['macd_signal'], enhanced_df['macd_histogram'] = calculate_macd(enhanced_df)
    
    # Add Bollinger Bands
    enhanced_df['bb_middle'], enhanced_df['bb_upper'], enhanced_df['bb_lower'] = calculate_bollinger_bands(enhanced_df)
    
    # Add Average True Range
    enhanced_df['atr_14'] = calculate_atr(enhanced_df, period=14)
    
    # Add daily returns
    enhanced_df['daily_return'] = enhanced_df['close'].pct_change()
    
    # Add rolling volatility (standard deviation of returns)
    enhanced_df['volatility_20'] = enhanced_df['daily_return'].rolling(window=20).std()
    
    return enhanced_df

def generate_trading_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trading signals based on technical indicators
    
    Args:
        df: DataFrame with price and technical indicator data
        
    Returns:
        DataFrame with added columns for trading signals
    """
    if df.empty:
        return df
        
    # Make a copy to avoid modifying the original
    signals_df = df.copy()
    
    # Add technical indicators if not already present
    if not all(col in signals_df.columns for col in ['sma_20', 'sma_50', 'rsi_14']):
        signals_df = enhance_dataframe(signals_df)
    
    # Initialize signal columns
    signals_df['signal_sma_crossover'] = 0
    signals_df['signal_rsi_oversold'] = 0
    signals_df['signal_rsi_overbought'] = 0
    signals_df['signal_macd_crossover'] = 0
    signals_df['signal_bb_bounce'] = 0
    
    # SMA crossover (SMA 20 crossing above SMA 50)
    if 'sma_20' in signals_df.columns and 'sma_50' in signals_df.columns:
        signals_df['signal_sma_crossover'] = np.where(
            (signals_df['sma_20'] > signals_df['sma_50']) & 
            (signals_df['sma_20'].shift(1) <= signals_df['sma_50'].shift(1)),
            1,  # Bullish signal
            np.where(
                (signals_df['sma_20'] < signals_df['sma_50']) & 
                (signals_df['sma_20'].shift(1) >= signals_df['sma_50'].shift(1)),
                -1,  # Bearish signal
                0    # No signal
            )
        )
    
    # RSI signals
    if 'rsi_14' in signals_df.columns:
        signals_df['signal_rsi_oversold'] = np.where(
            (signals_df['rsi_14'] < 30) & (signals_df['rsi_14'].shift(1) <= 30),
            1,  # Bullish signal (oversold)
            0   # No signal
        )
        signals_df['signal_rsi_overbought'] = np.where(
            (signals_df['rsi_14'] > 70) & (signals_df['rsi_14'].shift(1) >= 70),
            -1,  # Bearish signal (overbought)
            0    # No signal
        )
    
    # MACD crossover
    if all(col in signals_df.columns for col in ['macd_line', 'macd_signal']):
        signals_df['signal_macd_crossover'] = np.where(
            (signals_df['macd_line'] > signals_df['macd_signal']) & 
            (signals_df['macd_line'].shift(1) <= signals_df['macd_signal'].shift(1)),
            1,  # Bullish signal
            np.where(
                (signals_df['macd_line'] < signals_df['macd_signal']) & 
                (signals_df['macd_line'].shift(1) >= signals_df['macd_signal'].shift(1)),
                -1,  # Bearish signal
                0    # No signal
            )
        )
    
    # Bollinger Band bounce
    if all(col in signals_df.columns for col in ['close', 'bb_upper', 'bb_lower']):
        signals_df['signal_bb_bounce'] = np.where(
            (signals_df['close'] < signals_df['bb_lower']) & 
            (signals_df['close'].shift(1) <= signals_df['bb_lower'].shift(1)),
            1,  # Bullish signal (bounce from lower band)
            np.where(
                (signals_df['close'] > signals_df['bb_upper']) & 
                (signals_df['close'].shift(1) >= signals_df['bb_upper'].shift(1)),
                -1,  # Bearish signal (bounce from upper band)
                0    # No signal
            )
        )
    
    # Aggregate signals
    signals_df['signal_aggregate'] = (
        signals_df['signal_sma_crossover'] + 
        signals_df['signal_rsi_oversold'] + 
        signals_df['signal_rsi_overbought'] + 
        signals_df['signal_macd_crossover'] + 
        signals_df['signal_bb_bounce']
    )
    
    return signals_df

def get_daily_recommendation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get a daily trading recommendation based on technical analysis
    
    Args:
        df: DataFrame with price data
        
    Returns:
        Dictionary with recommendation and supporting data
    """
    if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        return {'recommendation': 'no_data', 'confidence': 0, 'signals': {}}
    
    # Get signals
    signals_df = generate_trading_signals(df)
    
    # Focus on the most recent data point
    latest_data = signals_df.iloc[-1]
    
    # Count positive and negative signals
    positive_signals = 0
    negative_signals = 0
    neutral_signals = 0
    
    signal_columns = [col for col in signals_df.columns if col.startswith('signal_') and col != 'signal_aggregate']
    
    signal_details = {}
    for signal in signal_columns:
        signal_value = latest_data[signal]
        signal_name = signal.replace('signal_', '')
        
        if signal_value > 0:
            positive_signals += 1
            signal_details[signal_name] = 'bullish'
        elif signal_value < 0:
            negative_signals += 1
            signal_details[signal_name] = 'bearish'
        else:
            neutral_signals += 1
            signal_details[signal_name] = 'neutral'
    
    # Determine overall recommendation
    total_signals = positive_signals + negative_signals
    if total_signals == 0:
        recommendation = 'neutral'
        confidence = 0
    else:
        positive_ratio = positive_signals / total_signals
        if positive_ratio >= 0.7:
            recommendation = 'strong_buy'
            confidence = min(positive_ratio * 100, 95)
        elif positive_ratio >= 0.5:
            recommendation = 'buy'
            confidence = positive_ratio * 100
        elif positive_ratio <= 0.3:
            recommendation = 'strong_sell'
            confidence = min((1 - positive_ratio) * 100, 95)
        elif positive_ratio <= 0.5:
            recommendation = 'sell'
            confidence = (1 - positive_ratio) * 100
        else:
            recommendation = 'neutral'
            confidence = 50
    
    # Get latest price and indicators
    price_data = {
        'close': latest_data['close'],
        'open': latest_data['open'],
        'high': latest_data['high'],
        'low': latest_data['low']
    }
    
    # Get indicator values if they exist
    indicators = {}
    indicator_columns = [
        'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
        'rsi_14', 'macd_line', 'macd_signal', 'macd_histogram',
        'bb_middle', 'bb_upper', 'bb_lower', 'atr_14'
    ]
    
    for indicator in indicator_columns:
        if indicator in latest_data:
            indicators[indicator] = latest_data[indicator]
    
    # Calculate support and resistance
    sr_levels = detect_support_resistance(df)
    
    return {
        'recommendation': recommendation,
        'confidence': round(confidence, 2),
        'price': price_data,
        'indicators': indicators,
        'signals': signal_details,
        'support_levels': sr_levels['support'],
        'resistance_levels': sr_levels['resistance'],
        'last_updated': datetime.now().isoformat()
    }

def perform_portfolio_simulation(df: pd.DataFrame, initial_capital: float = 100000.0, 
                                position_size: float = 0.1) -> Dict[str, Any]:
    """
    Perform a simple backtest simulation
    
    Args:
        df: DataFrame with price data and generated signals
        initial_capital: Initial capital for the simulation
        position_size: Size of each position as a fraction of capital
        
    Returns:
        Dictionary with simulation results
    """
    if df.empty or not all(col in df.columns for col in ['close']):
        return {
            'initial_capital': initial_capital,
            'final_capital': initial_capital,
            'return_pct': 0,
            'trades': 0,
            'win_rate': 0,
            'message': 'Insufficient data for simulation'
        }
    
    # Generate signals if not already present
    if 'signal_aggregate' not in df.columns:
        signals_df = generate_trading_signals(df)
    else:
        signals_df = df.copy()
    
    # Initialize simulation variables
    capital = initial_capital
    position = 0  # Shares held
    entry_price = 0
    trades = []
    trade_count = 0
    win_count = 0
    
    # Run simulation
    for i in range(1, len(signals_df)):
        prev_row = signals_df.iloc[i-1]
        curr_row = signals_df.iloc[i]
        
        # Check for entry/exit signals
        signal = prev_row['signal_aggregate']
        
        # Current market price
        price = curr_row['close']
        
        # Logic for entering a long position
        if position == 0 and signal > 1:
            # Calculate position size
            position_value = capital * position_size
            position = position_value / price
            entry_price = price
            
            trades.append({
                'date': curr_row.name.strftime('%Y-%m-%d'),
                'action': 'buy',
                'price': price,
                'shares': position,
                'value': position * price,
                'capital': capital - (position * price)
            })
            
        # Logic for exiting a long position
        elif position > 0 and (signal < -1 or i == len(signals_df) - 1):
            # Calculate profit/loss
            exit_value = position * price
            entry_value = position * entry_price
            profit_loss = exit_value - entry_value
            
            # Update capital
            capital += exit_value
            
            trades.append({
                'date': curr_row.name.strftime('%Y-%m-%d'),
                'action': 'sell',
                'price': price,
                'shares': position,
                'value': exit_value,
                'profit_loss': profit_loss,
                'capital': capital
            })
            
            # Update trade statistics
            trade_count += 1
            if profit_loss > 0:
                win_count += 1
            
            # Reset position
            position = 0
            entry_price = 0
    
    # Calculate performance metrics
    return_pct = ((capital - initial_capital) / initial_capital) * 100
    win_rate = (win_count / trade_count) * 100 if trade_count > 0 else 0
    
    # Generate benchmark comparison (buy and hold)
    if len(signals_df) > 1:
        first_price = signals_df.iloc[0]['close']
        last_price = signals_df.iloc[-1]['close']
        benchmark_return = ((last_price - first_price) / first_price) * 100
    else:
        benchmark_return = 0
    
    return {
        'initial_capital': initial_capital,
        'final_capital': capital,
        'return_pct': round(return_pct, 2),
        'benchmark_return_pct': round(benchmark_return, 2),
        'outperformance': round(return_pct - benchmark_return, 2),
        'trades': trade_count,
        'winning_trades': win_count,
        'win_rate': round(win_rate, 2) if trade_count > 0 else 0,
        'trade_history': trades[-10:],  # Return last 10 trades
        'start_date': signals_df.index[0].strftime('%Y-%m-%d'),
        'end_date': signals_df.index[-1].strftime('%Y-%m-%d')
    }


def generate_market_analysis_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive market analysis report

    Args:
        df: DataFrame with price data

    Returns:
        Dictionary with a comprehensive analysis report
    """
    if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        return {'status': 'error', 'message': 'Insufficient data for analysis'}

    # Add technical indicators
    enhanced_df = enhance_dataframe(df)

    # Generate trading signals
    signals_df = generate_trading_signals(enhanced_df)

    # Get recommendation
    recommendation = get_daily_recommendation(signals_df)

    # Get support and resistance levels
    sr_levels = detect_support_resistance(df)

    # Calculate Fibonacci levels
    fib_levels = calculate_fibonacci_levels(df)

    # Identify chart patterns
    patterns = identify_patterns(df)

    # Perform simulated backtest
    simulation = perform_portfolio_simulation(signals_df)

    # Get basic statistics
    stats = {
        'days': len(df),
        'start_date': df.index[0].strftime('%Y-%m-%d'),
        'end_date': df.index[-1].strftime('%Y-%m-%d'),
        'current_price': float(df['close'].iloc[-1]),
        'daily_change': float(df['close'].iloc[-1] - df['close'].iloc[-2]) if len(df) > 1 else 0,
        'daily_change_pct': float(df['close'].pct_change().iloc[-1] * 100) if len(df) > 1 else 0,
        'price_range': {
            'min': float(df['low'].min()),
            'max': float(df['high'].max()),
            'current_percentile': float(np.percentile(df['close'], 50))  # Current price percentile
        }
    }

    # Calculate trend statistics
    if len(df) >= 20:
        stats['trend'] = {
            'short_term': 'bullish' if df['close'].iloc[-1] > df['close'].iloc[-5] else 'bearish',
            'medium_term': 'bullish' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'bearish',
            'long_term': 'bullish' if len(df) > 50 and df['close'].iloc[-1] > df['close'].iloc[-50] else 'bearish'
        }

    # Calculate volatility
    if len(df) >= 20:
        returns = df['close'].pct_change().dropna()
        stats['volatility'] = {
            'daily': float(returns.std() * 100),  # Daily volatility
            'annualized': float(returns.std() * 100 * np.sqrt(252)),  # Annualized volatility
            'vs_market': 'high' if returns.std() > 0.02 else 'normal'  # Simple comparison
        }

    # Get indicator values for the most recent day
    latest_indicators = {col: float(signals_df[col].iloc[-1])
                         for col in signals_df.columns
                         if col.startswith(('sma_', 'ema_', 'rsi_', 'macd_', 'bb_', 'atr_'))
                         and not pd.isna(signals_df[col].iloc[-1])}

    # Compile report
    report = {
        'status': 'success',
        'basic_stats': stats,
        'recommendation': recommendation,
        'technical_indicators': latest_indicators,
        'support_resistance': sr_levels,
        'fibonacci_levels': fib_levels,
        'patterns': patterns,
        'simulation': simulation,
        'timestamp': datetime.now().isoformat()
    }

    # Add trend analysis
    if 'trend' in stats:
        # Determine trend strength
        trend_scores = {
            'bullish': 1,
            'bearish': -1
        }

        trend_strength = (
                trend_scores.get(stats['trend']['short_term'], 0) +
                trend_scores.get(stats['trend']['medium_term'], 0) * 2 +  # Medium term has double weight
                trend_scores.get(stats['trend']['long_term'], 0) * 3  # Long term has triple weight
        )

        if trend_strength >= 4:
            trend_analysis = "Strong bullish trend across multiple timeframes"
        elif trend_strength >= 2:
            trend_analysis = "Moderate bullish trend"
        elif trend_strength <= -4:
            trend_analysis = "Strong bearish trend across multiple timeframes"
        elif trend_strength <= -2:
            trend_analysis = "Moderate bearish trend"
        else:
            trend_analysis = "Mixed or sideways trend"

        report['trend_analysis'] = {
            'strength': trend_strength,
            'description': trend_analysis
        }

    # Add market context
    report['market_context'] = {
        'suggested_stop_loss': round(df['close'].iloc[-1] * 0.95, 2),  # Simple 5% stop loss
        'risk_level': 'high' if stats.get('volatility', {}).get('daily', 0) > 2 else 'medium',
        'trading_suggestion': 'Consider smaller position sizes due to high volatility'
        if stats.get('volatility', {}).get('daily', 0) > 2
        else 'Standard position sizing recommended'
    }

    # Add future price targets based on technical analysis
    report['price_targets'] = {
        'next_resistance': sr_levels['resistance'][0] if sr_levels['resistance'] else None,
        'next_support': sr_levels['support'][0] if sr_levels['support'] else None,
        'upside_potential': round((sr_levels['resistance'][0] / df['close'].iloc[-1] - 1) * 100, 2)
        if sr_levels['resistance'] else None,
        'downside_risk': round((1 - sr_levels['support'][0] / df['close'].iloc[-1]) * 100, 2)
        if sr_levels['support'] else None
    }

    return report