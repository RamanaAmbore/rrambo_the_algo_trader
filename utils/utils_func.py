import pyotp

from models.trades import Trades
from models.ledger_entries import LedgerEntries
from models.profit_loss import ProfitLoss
from utils.config_loader import Env


def generate_totp():
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(Env.TOTP_TOKEN).now()


def return_model_for_prefix(report_prefix):
    if report_prefix.startswith("tradebook"):
        model = Trades
    elif report_prefix.startswith("pnl"):
        model = ProfitLoss
    elif report_prefix.startswith("ledger"):
        model = LedgerEntries
    else:
        print("Unsupported file format!")
    return model
