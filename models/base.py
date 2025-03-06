from sqlalchemy.ext.declarative import declarative_base

from utils.logger import get_logger

"""
if you need to delete the tables:
drop table  access_token cascade;
drop table  backtest_results cascade;
drop table  algo_schedule cascade;
drop table  option_contracts cascade;
drop table  option_greeks cascade;
drop table  option_strategies cascade;
drop table  orders cascade;
drop table  holdings cascade;
drop table  positions cascade;
drop table  stock_list cascade;
drop table  strategy_config cascade;
drop table  trades cascade;
drop table  watchlists cascade;
drop table  watchlist_instruments cascade;
"""

logger = get_logger(__name__)
Base = declarative_base()
