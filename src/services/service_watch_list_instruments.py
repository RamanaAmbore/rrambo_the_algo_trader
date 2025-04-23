from typing import List, Optional, Dict, Any

from sqlalchemy import literal, union
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.core.singleton_base import SingletonBase
from src.helpers.database_manager import db
from src.helpers.logger import get_logger
from src.models.holdings import Holdings
from src.models.positions import Positions
from src.models.watch_list_instruments import WatchListInstruments
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceWatchListInstruments(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = WatchListInstruments
    conflict_cols = ['account', 'watchlist', 'tradingsymbol', 'exchange']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    async def get_watchlist_instrument_tokens(all_instruments):
        """Fetch unique instrument tokens for watchlist, positions, and holdings using Kite instrument list."""
        async with db.get_async_session() as session:
            try:
                # Step 1: Get distinct trading symbols, exchanges, accounts, and watchlists
                stmt = union(
                    # Watchlist: Use existing account and watchlist value
                    select(
                        WatchListInstruments.tradingsymbol,
                        WatchListInstruments.exchange,
                        WatchListInstruments.account,
                        WatchListInstruments.watchlist
                    ).distinct(),

                    # Positions: Fetch account number, add 'positions' as watchlist type
                    select(
                        Positions.tradingsymbol,
                        Positions.exchange,
                        Positions.account,
                        literal('POSITIONS').label("watchlist")
                    ).distinct(),

                    # Holdings: Fetch account number, add 'holdings' as watchlist type
                    select(
                        Holdings.tradingsymbol,
                        Holdings.exchange,
                        Holdings.account,
                        literal('HOLDINGS').label("watchlist")
                    ).distinct()
                )

                results = await session.execute(stmt)
                rec_fields = results.all()

                if not rec_fields:
                    logger.info("No symbols found in watchlist, positions, or holdings.")
                    return None, []

                # Convert Kite instrument list to a dictionary for quick lookup
                instrument_map = {
                    (inst['tradingsymbol'], inst['exchange']): inst['instrument_token']
                    for inst in all_instruments
                }

                # Fetch instrument tokens from the dictionary
                instrument_tokens = []
                for tradingsymbol, exchange, _, _ in rec_fields:
                    token = instrument_map.get((tradingsymbol, exchange))
                    if token:
                        instrument_tokens.append(token)
                    else:
                        logger.warning(f"Instrument token not found for {tradingsymbol} ({exchange})")

                logger.info(f"Fetched {len(instrument_tokens)} unique watch list instrument tokens.")
                return rec_fields, instrument_tokens

            except SQLAlchemyError as e:
                logger.error(f"Error fetching watch list instrument tokens: {e}", exc_info=True)
                return None, []

    async def update_watchlist_with_ohlc(results, instrument_tokens, ohlc_data):
        """Insert or update watchlist with instrument tokens and OHLC data."""
        if not ohlc_data:
            logger.info("No OHLC data available for update.")
            return

        records = []

        # Map instrument tokens from results
        for idx, inst in enumerate(instrument_tokens):
            ohlc = ohlc_data.get(str(inst))
            if ohlc:
                result = results[idx]
                last_price = ohlc.get("ohlc", {}).get('close')
                prev_close_price = ohlc.get('last_price')
                change = last_price - prev_close_price
                records.append({
                    "account": '*' if result[2] is None else result[2],
                    "watchlist": result[3],
                    "tradingsymbol": result[0],
                    "exchange": result[1],
                    "instrument_token": inst,
                    "last_price": last_price,
                    "prev_close_price": prev_close_price,
                    "change": change,
                    "change_percent": 0 if prev_close_price == 0 else (change / prev_close_price) * 100

                })

        if not records:
            logger.info("No valid OHLC data found for the watch list instruments.")
            return

        async with db.get_async_session() as session:
            try:
                # Upsert (Insert or Update)
                stmt = insert(WatchListInstruments).values(records)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["account", "watchlist", "tradingsymbol", "exchange"],  # Unique constraint fields
                    set_={
                        "instrument_token": stmt.excluded.instrument_token,
                        "last_price": stmt.excluded.last_price,
                        "prev_close_price": stmt.excluded.prev_close_price,
                        "change": stmt.excluded.change,
                        "change_percent": stmt.excluded.change_percent
                    }
                )

                await session.execute(stmt)
                await session.commit()
                logger.info(f"Updated OHLC data for {len(records)} watch list instruments.")

            except SQLAlchemyError as e:
                logger.error(f"Error updating watch list instruments table with OHLC data: {e}", exc_info=True)
                await session.rollback()

    async def setup_table_records(self, default_records: List[Dict[str, Any]],
                                  update_columns: Optional[List[str]] = None,
                                  exclude_from_update=('timestamp',),
                                  skip_update_if_exists: bool = False,
                                  ignore_extra_columns: bool = False,  # <-- New flag
                                  ) -> None:
        await super().setup_table_records(default_records,
                                          update_columns,
                                          exclude_from_update,
                                          skip_update_if_exists,
                                          ignore_extra_columns)


service_watch_list_instruments = ServiceWatchListInstruments()
