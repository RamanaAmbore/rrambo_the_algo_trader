from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

from utils.settings_loader import Env

Base = declarative_base()


def timestamp_indian():
    return datetime.now()  # You can adjust this function for Indian timezone


class Parameters(Base):
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    parameter = Column(String, nullable=False)
    parameter_value = Column(Numeric, nullable=False)

    timestamp = Column(DateTime, default=timestamp_indian, nullable=False)
    source = Column(String, nullable=False)
    warning_error = Column(String, nullable=True)
    msg = Column(String, nullable=True)

    @classmethod
    def fetch_by_user_id(cls, session: Session, user_id=Env.ZERODHA_USERNAME):
        return session.query(cls).filter_by(account_id=user_id).all()

    def __repr__(self):
        return f"<Parameters(id={self.id}, parameter='{self.parameter}', value={self.parameter_value}, account_id={self.account_id})>"
