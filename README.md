# Algo Trading Dashboard

This is an algorithmic trading dashboard for options trading using the Zerodha Kite Connect API. The application is built using **Python, Dash, and Plotly**, and provides real-time market data visualization and order management.

## Features
- **Live Market Data**: Displays real-time stock market data with interactive charts.
- **Holdings & Positions**: View current stock holdings and option positions.
- **Order Placement**: Place option trades directly from the dashboard.
- **Order Monitoring**: Track orders until execution.
- **Stop Loss & Position Adjustments**: Manage stop-loss orders and modify positions.
- **Automated Login**: Uses Selenium to log in and retrieve access tokens.
- **Secure Configuration Management**: Uses `.env` for secrets and `constants.yaml` for non-sensitive constants.
- **Logging System**:
  - Debug and above logs in `logs/debug.log`
  - Error logs in `logs/error.log`
  - Console logs debug and above messages
  
## Folder Structure
```
rrambo_trader/
│── .env                    # Stores API keys, secrets, and configuration parameters
│── .gitignore               # Ensure .env is not committed
│── app.py                   # Main Dash application (Landing Page with Live Chart)
│── requirements.txt         # Dependencies for the project
│
├───logs/                    
│   ├── debug.log            # Stores debug and above logs
│   ├── error.log            # Stores only error logs
│
├───config/                   # Constants Folder
│   ├── constants.yaml        # Stores non-sensitive constants
│
├───utils/                   
│   ├── logger.py            # Logger setup
│   ├── config_loader.py     # Loads environment variables from .env and constants from YAML
│
├───auth/                    
│   ├── login.py             # Automates Zerodha login using Selenium
│   ├── totp.py              # Generates TOTP for 2FA using PyOTP
│   ├── session.py           # Manages API session and access token
│
├───data/                    
│   ├── fetch_market_data.py # Fetches historical and live market data
│   ├── instruments.csv      # Zerodha instrument token mapping
│
└── README.md                # Project documentation
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rrambo_trader.git
cd rrambo_trader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root folder with the following content:
```env
# Zerodha Credentials
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_TOTP_SECRET=your_totp_secret
ZERODHA_USERNAME=your_zerodha_username
ZERODHA_PASSWORD=your_zerodha_password

# Logging Configuration
DEBUG_LOG_FILE=logs/debug.log
ERROR_LOG_FILE=logs/error.log
CONSOLE_LOG_LEVEL=DEBUG
FILE_LOG_LEVEL=DEBUG
ERROR_LOG_LEVEL=ERROR
```

# Algo Trading Dashboard

This is an algorithmic trading dashboard for options trading using the Zerodha Kite Connect API. The application is built using **Python, Dash, and Plotly**, and provides real-time market data visualization and order management.

## Features
- **Live Market Data**: Displays real-time stock market data with interactive charts.
- **Holdings & Positions**: View current stock holdings and option positions.
- **Order Placement**: Place option trades directly from the dashboard.
- **Order Monitoring**: Track orders until execution.
- **Stop Loss & Position Adjustments**: Manage stop-loss orders and modify positions.
- **Automated Login**: Uses Selenium to log in and retrieve access tokens.
- **Secure Configuration Management**: Uses `.env` for secrets and `constants.yaml` for non-sensitive constants.
- **Logging System**:
  - Debug and above logs in `logs/debug.log`
  - Error logs in `logs/error.log`
  - Console logs debug and above messages
  
## Folder Structure
```
rrambo_the_algo_trader/
│── .env                    # Stores API keys, secrets, and configuration parameters
│── .gitignore               # Ensure .env is not committed
│── app.py                   # Main Dash application (Landing Page with Live Chart)
│── requirements.txt         # Dependencies for the project
│
├───logs/                    
│   ├── debug.log            # Stores debug and above logs
│   ├── error.log            # Stores only error logs
│
├───config/                   # Constants Folder
│   ├── constants.yaml        # Stores non-sensitive constants
│
├───utils/                   
│   ├── logger.py            # Logger setup
│   ├── config_loader.py     # Loads environment variables from .env and constants from YAML
│
├───auth/                    
│   ├── login.py             # Automates Zerodha login using Selenium
│   ├── totp.py              # Generates TOTP for 2FA using PyOTP
│   ├── session.py           # Manages API session and access token
│
├───data/                    
│   ├── fetch_market_data.py # Fetches historical and live market data
│   ├── instruments.csv      # Zerodha instrument token mapping
│
└── README.md                # Project documentation
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rrambo_the_algo_trader.git
cd rrambo_the_algo_trader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root folder with the following content:
```env
# Zerodha Credentials
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_TOTP_SECRET=your_totp_secret
ZERODHA_USERNAME=your_zerodha_username
ZERODHA_PASSWORD=your_zerodha_password

# Logging Configuration
DEBUG_LOG_FILE=logs/debug.log
ERROR_LOG_FILE=logs/error.log
CONSOLE_LOG_LEVEL=DEBUG
FILE_LOG_LEVEL=DEBUG
ERROR_LOG_LEVEL=ERROR
```

### 4. Configure Constants
Create `config/constants.yaml` with non-sensitive values:
```yaml
market:
  instrument_token: 260105  # NIFTY 50
  data_fetch_interval: 5  # Time in seconds
```

### 5. Run the Application
```bash
python app.py
```
The application will start on **http://127.0.0.1:8050**.

## Logging Details
The logger is configured to:
- **Store all debug and above logs** in `logs/debug.log`
- **Store error logs only** in `logs/error.log`
- **Print debug logs to the console**

## Future Enhancements
- Implement **automated trading strategies**
- Add **web-based authentication** for multiple users
- Improve **order execution speed** with WebSockets

## License
This project is open-source and available under the MIT License.

---
If you have any issues, feel free to open an issue or contribute to the project!