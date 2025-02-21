import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from sqlalchemy import create_engine, Column, String, Float, Integer, Date
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import datetime
from layout import create_layout

app = dash.Dash(__name__,
                external_stylesheets=["https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"])
app.title = "NSE Stock Market Dashboard"

# Database Configuration
DB_FILE = "stocks.db"
engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


class StockPrice(Base):
    __tablename__ = 'stock_prices'
    symbol = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)


class StockList(Base):
    __tablename__ = 'stock_list'
    symbol = Column(String, primary_key=True)
    name = Column(String)
    last_updated = Column(Date)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def update_stock_list():
    """Fetch NSE stock list once a week and update the database."""
    session = Session()
    last_update = session.query(StockList).order_by(StockList.last_updated.desc()).first()
    if last_update and (datetime.date.today() - last_update.last_updated).days < 7:
        session.close()
        return

    stock_symbols = ["RELIANCE.NS", "TATAMOTORS.NS", "INFY.NS", "HDFCBANK.NS", "TCS.NS"]  # Replace with full list
    session.query(StockList).delete()
    for symbol in stock_symbols:
        session.add(StockList(symbol=symbol, name=symbol, last_updated=datetime.date.today()))
    session.commit()
    session.close()


def get_stock_data(symbol, period="7d", interval="1d"):
    """Fetch stock data from database or Yahoo Finance."""
    session = Session()
    data = session.query(StockPrice).filter(StockPrice.symbol == symbol).order_by(StockPrice.date.desc()).limit(7).all()
    session.close()

    if data:
        df = pd.DataFrame([(d.symbol, d.date, d.open, d.high, d.low, d.close, d.volume) for d in data],
                          columns=["symbol", "Date", "Open", "High", "Low", "Close", "Volume"])
        df.set_index("Date", inplace=True)
        return df
    else:
        df = yf.download(symbol, period=period, interval=interval)
        df.reset_index(inplace=True)

        session = Session()
        for _, row in df.iterrows():
            session.add(StockPrice(symbol=symbol, date=row['Date'], open=row['Open'], high=row['High'],
                                   low=row['Low'], close=row['Close'], volume=row['Volume']))
        session.commit()
        session.close()
        return df


def get_stock_info(symbol):
    """Fetch stock fundamental data from Yahoo Finance."""
    stock = yf.Ticker(symbol)
    info = stock.info
    return {
        "Sector": info.get("sector", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "PE Ratio": info.get("trailingPE", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A")
    }


# Update stock list once a week
update_stock_list()

session = Session()
stocks = session.query(StockList).all()
stock_options = [{'label': stock.name, 'value': stock.symbol} for stock in stocks]
session.close()

app.layout = create_layout(stock_options)


@app.callback(
    Output('market-graph', 'figure'),
    [Input('stock-dropdown', 'value'), Input('tabs', 'value')]
)
def update_graph(selected_stock, selected_tab):
    """Update stock chart based on selected stock and tab."""
    if selected_tab == 'historical':
        df = get_stock_data(selected_stock)
    else:
        df = yf.download(selected_stock, period="1d", interval="1m")

    figure = {
        'data': [go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=selected_stock
        )],
        'layout': go.Layout(title=f"Stock Market Data for {selected_stock}", xaxis_title='Date', yaxis_title='Price')
    }
    return figure


@app.callback(
    Output('stock-info', 'children'),
    [Input('stock-dropdown', 'value')]
)
def update_stock_info(selected_stock):
    """Update stock fundamental details."""
    info = get_stock_info(selected_stock)
    return html.Div([
        html.P(f"Sector: {info['Sector']}", className="mt-2"),
        html.P(f"Market Cap: {info['Market Cap']}", className="mt-2"),
        html.P(f"PE Ratio: {info['PE Ratio']}", className="mt-2"),
        html.P(f"Dividend Yield: {info['Dividend Yield']}", className="mt-2")
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
