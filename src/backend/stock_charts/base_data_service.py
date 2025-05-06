# src/stock_charts/base_data_service.py
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple

from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class BaseDataService(SingletonBase):
    """Base class for data services with common functionality for DataFrame persistence and caching."""

    def __init__(self, data_dir_name: str):
        """
        Initialize the base data service

        Args:
            data_dir_name: Name of the subdirectory to store data files
        """
        self._base_data_dir = os.path.join(os.path.dirname(__file__), '../../data/stock_charts')
        self._data_dir = os.path.join(self._base_data_dir, data_dir_name)
        os.makedirs(self._data_dir, exist_ok=True)
        self._data_cache = {}  # Cache for DataFrames

    def get_dataframe(self, cache_key: str) -> pd.DataFrame:
        """
        Get a DataFrame from the cache, or load it if not cached

        Args:
            cache_key: Unique identifier for the data

        Returns:
            DataFrame with the requested data
        """
        # Load data if not in memory
        if cache_key not in self._data_cache:
            self._load_data(cache_key)

        # Return a copy to prevent accidental modification
        return self._data_cache.get(cache_key, pd.DataFrame()).copy()

    def _get_file_path(self, cache_key: str) -> str:
        """
        Get the file path for a given cache key

        Args:
            cache_key: Unique identifier for the data

        Returns:
            Path to the data file
        """
        return os.path.join(self._data_dir, f"{cache_key}.json")

    def _save_data(self, cache_key: str, df: pd.DataFrame):
        """
        Save DataFrame to disk and update cache

        Args:
            cache_key: Unique identifier for the data
            df: DataFrame to save
        """
        try:
            if df.empty:
                return

            # Reset index to convert timestamp index to column
            df_to_save = df.reset_index()

            # Convert to dictionary format for JSON serialization
            json_data = df_to_save.to_dict(orient='records')

            # Add timestamp for when this data was saved
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "data": json_data
            }

            file_path = self._get_file_path(cache_key)
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            # Update cache
            self._data_cache[cache_key] = df

            logger.debug(f"Saved data for {cache_key}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error saving data for {cache_key}: {e}", exc_info=True)

    def _load_data(self, cache_key: str) -> pd.DataFrame:
        """
        Load data from disk if available and return as DataFrame

        Args:
            cache_key: Unique identifier for the data

        Returns:
            DataFrame with the loaded data
        """
        try:
            file_path = self._get_file_path(cache_key)

            if not os.path.exists(file_path):
                logger.warning(f"No cached data found for {cache_key}")
                self._data_cache[cache_key] = pd.DataFrame()
                return pd.DataFrame()

            with open(file_path, 'r') as f:
                data = json.load(f)

            # Convert to DataFrame
            json_data = data.get("data", [])
            if not json_data:
                self._data_cache[cache_key] = pd.DataFrame()
                return pd.DataFrame()

            df = pd.DataFrame(json_data)

            # Convert date column to datetime and set as index
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)

            # Sort by index
            if not df.empty:
                df.sort_index(inplace=True)

            # Update cache
            self._data_cache[cache_key] = df

            logger.info(f"Loaded cached data for {cache_key}: {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"Error loading data for {cache_key}: {e}", exc_info=True)
            self._data_cache[cache_key] = pd.DataFrame()
            return pd.DataFrame()

    def _merge_dataframes(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge two DataFrames, removing duplicates and sorting by index

        Args:
            existing_df: Existing DataFrame
            new_df: New DataFrame to merge

        Returns:
            Combined DataFrame
        """
        if existing_df.empty:
            return new_df

        if new_df.empty:
            return existing_df

        # Combine existing and new data
        combined_df = pd.concat([existing_df, new_df])

        # Remove duplicates based on index (timestamp)
        combined_df = combined_df[~combined_df.index.duplicated(keep='last')]

        # Sort by timestamp
        combined_df.sort_index(inplace=True)

        return combined_df

    def clear_cache(self):
        """Clear the in-memory cache"""
        self._data_cache.clear()
        logger.debug("Data cache cleared")

    def _format_data_for_charts(self, df: pd.DataFrame) -> List[Dict]:
        """
        Format DataFrame for chart libraries

        Args:
            df: DataFrame with OHLC data

        Returns:
            List of dictionaries formatted for charts
        """
        if df.empty:
            return []

        # Format for charting libraries
        formatted_data = []

        # Reset index to get timestamp as column
        df_with_date = df.reset_index()

        # Convert each row to a dictionary for the API
        for _, row in df_with_date.iterrows():
            candle = {
                "timestamp": row['date'].isoformat(),
                "open": row.get('open'),
                "high": row.get('high'),
                "low": row.get('low'),
                "close": row.get('close'),
                "volume": row.get('volume')
            }
            formatted_data.append(candle)

        return formatted_data