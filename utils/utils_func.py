from decimal import Decimal, ROUND_DOWN

import pyotp

from models.report_tradebook import ReportTradebook
from models.report_ledger_entries import ReportLedgerEntries
from models.report_profit_loss import ReportProfitLoss
from utils.parms import Parms


def generate_totp(totp_key):
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(totp_key).now()


def return_model_for_prefix(report_prefix):
    if report_prefix.startswith("tradebook"):
        model = ReportTradebook
    elif report_prefix.startswith("pnl"):
        model = ReportProfitLoss
    elif report_prefix.startswith("ledger"):
        model = ReportLedgerEntries
    else:
        print("Unsupported file format!")
    return

def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with 4 decimal places for option Greeks."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


