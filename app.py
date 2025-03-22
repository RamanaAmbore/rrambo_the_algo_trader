import dash
import dash_html_components as html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.graph_objs as go 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
from layout import create_layout
from src.models import StockList, get_stock_data, get_stock_info

app = dash.Dash()
app.title = "RRambo - Stock Market Dashboard"

# Database Configuration
DB_FILE = "stocks.db"
engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()

Base.metadata.create_all(engine)
Base.metadata.drop_all(engine)
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
    for tradingsymbol in stock_symbols:
        session.add(StockList(tradingsymbol=tradingsymbol, name=tradingsymbol, last_updated=datetime.date.today()))
    session.commit()
    session.close()


# Update stock list once a week
update_stock_list()

session = Session()
stocks = session.query(StockList).all()
stock_options = [{'label': stock.name, 'value': stock.tradingsymbol} for stock in stocks]
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
