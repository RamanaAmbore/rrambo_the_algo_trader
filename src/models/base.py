from sqlalchemy.ext.declarative import declarative_base

from src.helpers.logger import get_logger

"""
if you need to delete the tables:
drop table  access_tokens cascade;
drop table  backtest_results cascade;
drop table  schedule_time cascade;
drop table  schedule_list cascade;
drop table  option_contracts cascade;
drop table  option_greeks cascade;
drop table  orders cascade;
drop table  holdings cascade;
drop table  positions cascade;
drop table  instrument_list cascade;
drop table  strategy_config cascade;
drop table  trades cascade;
drop table  watch_list cascade;
drop table  watchlist_instruments cascade;
drop table  BrokerAccounts cascade;
drop table  report_ledger_entries cascade;
drop table  report_tradebook cascade;
drop table  refresh_flags cascade;
drop table  settings cascade;
"""

logger = get_logger(__name__)
Base = declarative_base()
