from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.services.service_access_tokens import service_access_tokens
from src.services.service_broker_accounts import service_broker_accounts
from src.services.service_parameter_table import service_parameter_table
from src.settings.constants_manager import DEF_PARAMETERS, DEF_BROKER_ACCOUNTS, DEF_ACCESS_TOKENS
from src.settings.parameter_manager import refresh_parameters


async def setup_parameters():
    # Step 1: Set up broker and parameter records
    await service_broker_accounts.setup_table_records(DEF_BROKER_ACCOUNTS, skip_update_if_exists=True)
    await service_parameter_table.setup_table_records(DEF_PARAMETERS, skip_update_if_exists=True)

    # Step 2: Set up access token records
    await service_access_tokens.setup_table_records(DEF_ACCESS_TOKENS, skip_update_if_exists=True)

    # Step 3: Refresh parameters
    records = await service_parameter_table.get_all_records()
    refresh_parameters(records, refresh=True)

    # Step 4: Initialize singleton instance
    ZerodhaKiteConnect().get_kite_conn(test_conn=True)

def get_kite_conn():
    return ZerodhaKiteConnect().get_kite_conn()

