# src/stock_charts/historical_data_service.py
from datetime import datetime
from typing import Dict, List, Union

import pandas as pd

from src.backend.stock_charts.base_data_service import BaseDataService
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class HistoricalDataService(BaseDataService):
    def __init__(self):
        super().__init__(data_dir_name='historical')

    def fetch_historical_data(self, kite_client, instrument_token: int,
                              interval: str, from_date: Union[datetime, str],
                              to_date: Union[datetime, str], continuous: bool = False) -> pd.DataFrame:
        """
        Fetch historical data from Kite API

        Args:
            kite_client: Authenticated Kite client instance
            instrument_token: Instrument identifier
            interval: Candle interval (minute, day, 3minute, etc.)
            from_date: Start date (datetime or string in format "YYYY-MM-DD HH:MM:SS")
            to_date: End date (datetime or string in format "YYYY-MM-DD HH:MM:SS")
            continuous: Get continuous data (across futures contracts for F&O)

        Returns:
            DataFrame of OHLC candles
        """
        logger.info(f"Fetching historical data for instrument {instrument_token}, interval {interval}")
        cache_key = f"{instrument_token}_{interval}"

        try:
            # Convert datetime objects to strings if needed
            if isinstance(from_date, datetime):
                from_date = from_date.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(to_date, datetime):
                to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")

            # Fetch data from Kite API
            historical_data = kite_client.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
                continuous=continuous
            )

            # Convert to DataFrame
            if historical_data:
                df = pd.DataFrame(historical_data)
                # Ensure date column is datetime type
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.sort_index(inplace=True)
            else:
                df = pd.DataFrame()

            # Save the data
            self._save_data(cache_key, df)

            logger.info(f"Successfully fetched {len(df)} candles for {instrument_token}")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}", exc_info=True)
            # Try to load from cache if fetch fails
            return self.get_dataframe(cache_key)

    def fetch_and_update_historical_data(self, kite_client, instrument_token: int,
                                         interval: str, from_date: Union[datetime, str],
                                         to_date: Union[datetime, str], continuous: bool = False) -> pd.DataFrame:
        """
        Fetch new historical data and merge with existing cached data

        Args:
            kite_client: Authenticated Kite client instance
            instrument_token: Instrument identifier
            interval: Candle interval (minute, day, 3minute, etc.)
            from_date: Start date (datetime or string in format "YYYY-MM-DD HH:MM:SS")
            to_date: End date (datetime or string in format "YYYY-MM-DD HH:MM:SS")
            continuous: Get continuous data (across futures contracts for F&O)

        Returns:
            Updated DataFrame of OHLC candles
        """
        cache_key = f"{instrument_token}_{interval}"

        # Load existing data
        existing_df = self.get_dataframe(cache_key)

        try:
            # Fetch new data
            new_df = self.fetch_historical_data(
                kite_client, instrument_token, interval, from_date, to_date, continuous
            )

            # Merge data and save
            combined_df = self._merge_dataframes(existing_df, new_df)

            if not combined_df.equals(existing_df):
                self._save_data(cache_key, combined_df)

            logger.info(f"Successfully updated historical data for {cache_key}, now have {len(combined_df)} candles")
            return combined_df

        except Exception as e:
            logger.error(f"Error updating historical data: {e}", exc_info=True)
            return existing_df

    def get_historical_dataframe(self, instrument_token: int, interval: str = "day") -> pd.DataFrame:
        """
        Get historical data as a DataFrame

        Args:
            instrument_token: Instrument identifier
            interval: Candle interval (minute, day, 3minute, etc.)

        Returns:
            DataFrame with OHLC candles
        """
        cache_key = f"{instrument_token}_{interval}"
        return self.get_dataframe(cache_key)

    def get_formatted_historical_data(self, instrument_token: int, interval: str = "day") -> List[Dict]:
        """
        Get historical data in a format suitable for charts

        Args:
            instrument_token: Instrument identifier
            interval: Candle interval (minute, day, 3minute, etc.)

        Returns:
            List of formatted data points for charting
        """
        # Get data as DataFrame
        df = self.get_historical_dataframe(instrument_token, interval)
        return self._format_data_for_charts(df)

    def perform_analysis(self, instrument_token: int, interval: str = "day") -> Dict:
        """
        Perform basic analysis on historical data

        Args:
            instrument_token: Instrument identifier
            interval: Candle interval (minute, day, 3minute, etc.)

        Returns:
            Dictionary with analysis results
        """
        df = self.get_historical_dataframe(instrument_token, interval)

        if df.empty:
            return {"status": "no_data"}

        analysis = {}

        # Basic statistics
        analysis["start_date"] = df.index[0].strftime("%Y-%m-%d")
        analysis["end_date"] = df.index[-1].strftime("%Y-%m-%d")
        analysis["days"] = len(df)

        # Price statistics
        if 'close' in df.columns:
            analysis["current_price"] = float(df['close'].iloc[-1])
            analysis["max_price"] = float(df['high'].max())
            analysis["min_price"] = float(df['low'].min())
            analysis["price_range"] = float(df['high'].max() - df['low'].min())

            # Calculate returns
            df['returns'] = df['close'].pct_change()
            analysis["daily_returns"] = {
                "mean": float(df['returns'].mean()),
                "std": float(df['returns'].std()),
                "positive_days": int((df['returns'] > 0).sum()),
                "negative_days": int((df['returns'] < 0).sum())
            }

            # Calculate moving averages
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['MA200'] = df['close'].rolling(window=200).mean()

            # Check for golden/death cross
            if not df['MA50'].empty and not df['MA200'].empty:
                if df['MA50'].iloc[-1] > df['MA200'].iloc[-1] and df['MA50'].iloc[-2] <= df['MA200'].iloc[-2]:
                    analysis["ma_signal"] = "golden_cross"
                elif df['MA50'].iloc[-1] < df['MA200'].iloc[-1] and df['MA50'].iloc[-2] >= df['MA200'].iloc[-2]:
                    analysis["ma_signal"] = "death_cross"
                else:
                    analysis["ma_signal"] = "none"

            # Current MA values
            analysis["moving_averages"] = {
                "MA50": float(df['MA50'].iloc[-1]) if not df['MA50'].empty else None,
                "MA200": float(df['MA200'].iloc[-1]) if not df['MA200'].empty else None
            }

        # Volume analysis
        if 'volume' in df.columns:
            analysis["volume"] = {
                "average": float(df['volume'].mean()),
                "max": float(df['volume'].max()),
                "current": float(df['volume'].iloc[-1]),
                "trend": "increasing" if df['volume'].iloc[-1] > df['volume'].iloc[-5:].mean() else "decreasing"
            }

        return analysis