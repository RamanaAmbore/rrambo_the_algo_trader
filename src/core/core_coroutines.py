from src.services.service_broker_accounts import service_broker_accounts
from src.services.service_parameter_table import service_parameter_table
from src.settings.constants_manager import DEF_PARAMETERS, DEF_BROKER_ACCOUNTS
from src.settings.parameter_manager import refresh_parameters


async def setup_parameters():
    await service_broker_accounts.setup_table_records(DEF_BROKER_ACCOUNTS, skip_update_if_exists=True)
    await service_parameter_table.setup_table_records(DEF_PARAMETERS, skip_update_if_exists=True)
    records = await service_parameter_table.get_all_records()
    refresh_parameters(records, refresh=True)
