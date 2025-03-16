import asyncio
import os
import re

import pandas as pd

from src.services.report_ledger_entries_service import ReportLedgerEntriesService
from src.services.report_profit_loss_service import ReportProfitLossService
from src.services.report_tradebook_service import ReportTradebookService
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager as Parms, sc
from src.utils.utils import read_file_content

logger = get_logger(__name__)


class ReportUploader:
    _initialized = False

    @classmethod
    def __initialize(cls, refresh=False):
        """Handles report file processing and database uploads."""
        if cls._initialized and not refresh:
            return
        cls._initialized = True
        logger.info("ReportUploader initialized")

    @classmethod
    async def upload_reports(cls):
        """Main function to process reports."""
        try:
            cls.__initialize()  # Ensure one-time setup

            refresh_reports = {
                "tradebook": Parms.REFRESH_TRADEBOOK,
                "pnl": Parms.REFRESH_PNL,
                "ledger": Parms.REFRESH_LEDGER
            }

            regex_patterns = {
                "tradebook": sc.REPORTS_PARM["TRADEBOOK"]["file_regex"],
                "pnl": sc.REPORTS_PARM["PNL"]["file_regex"],
                "ledger": sc.REPORTS_PARM["LEDGER"]["file_regex"]
            }

            service_xref = {
                "tradebook": ReportTradebookService,
                "pnl": ReportProfitLossService,
                "ledger": ReportLedgerEntriesService
            }

            all_files = os.listdir(Parms.DOWNLOAD_DIR)

            for key, pattern in regex_patterns.items():
                if not refresh_reports[key]:
                    continue

                compiled_pattern = re.compile(pattern)
                data_records = pd.DataFrame()  # Initialize as empty DataFrame

                for file_name in all_files:
                    match = compiled_pattern.match(file_name)
                    if match:
                        file_extension = match.groups()[-1]  # Last group is extension
                        file_content = read_file_content(os.path.join(Parms.DOWNLOAD_DIR, file_name), file_extension)

                        if isinstance(file_content, pd.DataFrame):
                            file_content = file_content.assign(account=match.group(1))

                        data_records = pd.concat([data_records, file_content], ignore_index=True)

                if not data_records.empty:
                    service = service_xref[key]
                    await service.bulk_insert_report_records(data_records)
                    logger.info(f"Uploaded {len(data_records)} records for {key}.")
                else:
                    logger.info(f"No new records found for {key}.")

            logger.info("Report upload process completed")
        except Exception:
            logger.exception("Main process failed")
            raise


if __name__ == "__main__":
    asyncio.run(ReportUploader.upload_reports())
