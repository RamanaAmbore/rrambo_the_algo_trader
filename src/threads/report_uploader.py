import asyncio
import os
import re

import pandas as pd

from src.services.report_ledger_entries_service import ReportLedgerEntriesService
from src.services.report_profit_loss_service import ReportProfitLossService
from src.services.report_tradebook_service import ReportTradebookService
from src.helpers.logger import get_logger
from src.settings.parameter_manager import parms
from src.settings import constants_manager as const
from src.helpers.utils import read_file_content

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
                "tradebook": parms.REFRESH_TRADEBOOK,
                "pnl": parms.REFRESH_PNL,
                "ledger": parms.REFRESH_LEDGER
            }

            regex_patterns = {
                "tradebook": const.REPORT["TRADEBOOK"]["file_regex"],
                "pnl": const.REPORT["PNL"]["file_regex"],
                "ledger": const.REPORT["LEDGER"]["file_regex"]
            }

            service_xref = {
                "tradebook": ReportTradebookService,
                "pnl": ReportProfitLossService,
                "ledger": ReportLedgerEntriesService
            }

            all_files = sorted(os.listdir(parms.REPORT_DOWNLOAD_DIR), key=lambda x: x.replace('.csv', '').replace('xlsx', ''))
            tasks = []

            for key, pattern in regex_patterns.items():
                if not refresh_reports[key]:
                    continue

                compiled_pattern = re.compile(pattern)
                data_records = pd.DataFrame()

                for file_name in all_files:
                    match = compiled_pattern.match(file_name)
                    if match:
                        file_extension = match.groups()[-1]
                        data_df = read_file_content(os.path.join(parms.REPORT_DOWNLOAD_DIR, file_name), file_extension)
                        print(data_df)
                        data_df = data_df.applymap(lambda x: None if pd.isna(x) else x)

                        if data_df is None or data_df.empty:
                            logger.warning(f"No data in {file_name}")
                            continue

                        if key == 'pnl':
                            try:
                                header_row_idx = data_df[data_df["Unnamed: 1"] == "Symbol"].index[0]
                                data_df.columns = data_df.iloc[header_row_idx]
                                data_df = data_df.iloc[header_row_idx + 1:].reset_index(drop=True)
                            except IndexError:
                                logger.warning(f"Header row missing in {file_name}")
                                continue

                        data_df = data_df.assign(account=match.group(2))
                        data_df.columns = (
                            data_df.columns.str.lower()
                            .str.replace(".", "", regex=False)
                            .str.replace("&", "n", regex=False)
                            .str.replace(r"[ &]+", "_", regex=True)
                        )
                        data_records = pd.concat([data_records, data_df], ignore_index=True)

                if not data_records.empty:
                    service = service_xref[key]()
                    tasks.append(service.bulk_insert_report_records(data_records))

            await asyncio.gather(*tasks)
            logger.info("Report upload process completed")

        except Exception as e:
            logger.exception(f"Main process failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(ReportUploader.upload_reports())
