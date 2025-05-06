# src/stock_charts/intraday_data_service.py
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Union

import pandas as pd

from src.backend.stock_charts.base_data_service import BaseDataService
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class IntradayDataService(BaseDataService):
    def __init__(self):
        super().__init__(data_dir_name='intraday')
        self._last_timestamp = {}  # instrument_token -> last fetched timestamp

    def _get_ohlc_cache_key(self, instrument_token: int) -> str:
        """Get cache key for OHLC data"""
        today = date.today().strftime("%Y-%m-%d")
        return f"{instrument_token}_{today}_ohlc"

    def _get_tick_cache_key(self, instrument_token: int) -> str:
        """Get cache key for tick data"""
        today = date.today().strftime("%Y-%m-%d")
        return f"{instrument_token}_{today}_ticks"

    def fetch_today_data(self, kite_client, instrument_token: int, force_full_refresh=False) -> pd.DataFrame:
        """
        Fetch today's intraday data using historical API.
        Only fetches data since the last timestamp if available, unless force_full_refresh is True.

        Args:
            kite_client: Authenticated Kite client instance
            instrument_token: Instrument identifier
            force_full_refresh: If True, fetch the entire day's data regardless of what's cached

        Returns:
            DataFrame of OHLC candles for today
        """
        logger.info(f"Fetching today's data for instrument {instrument_token}")
        cache_key = self._get_ohlc_cache_key(instrument_token)

        try:
            # Get today's date
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")
            current_time = datetime.now().strftime('%H:%M:%S')

            # Load existing data if not already in memory
            existing_df = self.get_dataframe(cache_key)

            # Determine from_date based on last timestamp or use market open
            from_date = f"{today_str} 09:15:00"  # Market open time (default)

            if not force_full_refresh and instrument_token in self._last_timestamp:
                # Get the last timestamp we have data for
                last_ts = self._last_timestamp[instrument_token]

                # Only fetch from the next minute after the last timestamp
                if isinstance(last_ts, datetime):
                    # Add 1 minute to avoid duplicate data
                    next_minute = last_ts + timedelta(minutes=1)
                    if next_minute.date() == today:  # Only if it's still today
                        from_date = next_minute.strftime("%Y-%m-%d %H:%M:%S")
                        logger.debug(f"Fetching incremental data from {from_date}")

            # Fetch new data from Kite API
            logger.debug(f"Fetching data from {from_date} to {today_str} {current_time}")
            new_data = kite_client.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=f"{today_str} {current_time}",
                interval="minute"
            )

            # Convert new data to DataFrame
            if new_data:
                new_df = pd.DataFrame(new_data)
                # Ensure date column is datetime type
                new_df['date'] = pd.to_datetime(new_df['date'])
                new_df.set_index('date', inplace=True)
            else:
                new_df = pd.DataFrame()

            if force_full_refresh or existing_df.empty:
                # Replace existing data with new data
                combined_df = new_df
            else:
                # Combine existing data with new data
                combined_df = self._merge_dataframes(existing_df, new_df)
                logger.debug(f"Added {len(new_df)} new data points to existing {len(existing_df)}")

            # Update the last timestamp
            if not combined_df.empty:
                self._last_timestamp[instrument_token] = combined_df.index[-1].to_pydatetime()
                logger.debug(f"Updated last timestamp to {self._last_timestamp[instrument_token]}")

            # Save the combined data
            self._save_data(cache_key, combined_df)

            logger.info(f"Successfully fetched intraday data, now have {len(combined_df)} minute candles for today")
            return combined_df

        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}", exc_info=True)
            # Return the cached data if fetch fails
            return self.get_dataframe(cache_key)

    def append_tick_data(self, instrument_token: int, price: float, timestamp: Union[datetime, str],
                         volume: Optional[int] = None):
        """
        Append a new tick to the intraday data
        Note: Ticks are stored separately from OHLC data

        Args:
            instrument_token: Instrument identifier
            price: Last traded price
            timestamp: Timestamp of the tick
            volume: Last traded quantity
        """
        cache_key = self._get_tick_cache_key(instrument_token)

        # Ensure we have a tick cache for this instrument
        ticks_df = self.get_dataframe(cache_key)

        # Convert timestamp to datetime if it's a string
        if isinstance(timestamp, str):
            try:
                timestamp = pd.to_datetime(timestamp)
            except:
                timestamp = pd.Timestamp.now()
        elif not isinstance(timestamp, (datetime, pd.Timestamp)):
            timestamp = pd.Timestamp.now()

        # Create new data point as a Series
        tick_data = pd.Series({
            'price': price,
            'volume': volume
        }, name=timestamp)

        # Append to DataFrame
        ticks_df = pd.concat([
            ticks_df,
            pd.DataFrame([tick_data])
        ])

        # Save ticks periodically (e.g., every 10 ticks)
        if len(ticks_df) % 10 == 0:
            self._save_data(cache_key, ticks_df)

    def get_intraday_dataframe(self, instrument_token: int) -> pd.DataFrame:
        """
        Get intraday OHLC data as DataFrame

        Args:
            instrument_token: Instrument identifier

        Returns:
            DataFrame with OHLC candles
        """
        cache_key = self._get_ohlc_cache_key(instrument_token)
        return self.get_dataframe(cache_key)

    def get_tick_dataframe(self, instrument_token: int) -> pd.DataFrame:
        """
        Get tick data as DataFrame

        Args:
            instrument_token: Instrument identifier

        Returns:
            DataFrame with tick data
        """
        cache_key = self._get_tick_cache_key(instrument_token)
        return self.get_dataframe(cache_key)

    def get_formatted_intraday_data(self, instrument_token: int) -> List[Dict]:
        """
        Get intraday data in a format suitable for charts.
        Combines OHLC candles and recent ticks.

        Args:
            instrument_token: Instrument identifier

        Returns:
            List of formatted data points for charting
        """
        # Get OHLC data as DataFrame
        ohlc_df = self.get_intraday_dataframe(instrument_token)

        # Get tick data as DataFrame
        tick_df = self.get_tick_dataframe(instrument_token)

        # Format OHLC data for charting libraries
        formatted_data = self._format_data_for_charts(ohlc_df)

        # Find the most recent candle timestamp
        last_candle_timestamp = None
        if not ohlc_df.empty:
            last_candle_timestamp = ohlc_df.index[-1]

        # Add ticks that are newer than the last OHLC candle
        if last_candle_timestamp is not None and not tick_df.empty:
            # Filter ticks to only include those after the last candle
            recent_ticks = tick_df[tick_df.index > last_candle_timestamp]

            if not recent_ticks.empty:
                # Reset index to get timestamp as column
                recent_ticks = recent_ticks.reset_index()

                # Convert each tick to a dictionary for the API
                for _, tick in recent_ticks.iterrows():
                    tick_data = {
                        "timestamp": tick['index'].isoformat(),
                        "price": tick.get('price'),
                        "volume": tick.get('volume'),
                        "is_tick": True
                    }
                    formatted_data.append(tick_data)

        return formatted_data

    def clear_old_data(self):
        """Clear data from previous trading days"""
        today = date.today().strftime("%Y-%m-%d")

        try:
            for filename in os.listdir(self._data_dir):
                # Skip files from today
                if today in filename:
                    continue

                # Remove old files
                file_path = os.path.join(self._data_dir, filename)
                os.remove(file_path)
                logger.debug(f"Removed old data file: {filename}")
        except Exception as e:
            logger.error(f"Error clearing old data: {e}", exc_info=True)