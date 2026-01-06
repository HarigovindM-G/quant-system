# HakuQuant

Quantitative Trading Library for systematic trading strategies.

## Installation

1. Install the package in editable mode:

```bash
pip install -e .
```

## Database Storage

This project uses **SQLite** to store historical market data in a `.db` file within the repository. No external database setup required!

The database file is stored at `Data/hakuquant.db` and is automatically created when you run the application.

## Usage

### Fetching and Storing Market Data

The main script pulls OHLCV data from OANDA and stores it in SQLite:

```bash
python main.py
```

This will:

1. Fetch OHLCV data for all configured instruments from OANDA
2. Create a combined DataFrame with format: `{instrument} {column_name}`
3. Store the data in SQLite database at `Data/hakuquant.db`

### Importing the Package

After installation with `pip install -e .`, you can import modules:

```python
from quantlib.data import get_sp500_tickers, get_sp500_df
from quantlib.database import Database
from quantlib import general_utils as gu

# Fetch S&P 500 data
df, instruments = get_sp500_df()

# Save/load data with pickle
gu.save_file('./Data/mydata.obj', (df, instruments))
loaded_data = gu.load_file('./Data/mydata.obj')

# Database operations
db = Database('Data/hakuquant.db')
db.save_dataframe(df, 'my_table')
loaded_df = db.load_dataframe('my_table')
db.close()
```

### Working with the Database

```python
from quantlib.database import Database

# Connect to database
db = Database('Data/hakuquant.db')

# Load OANDA data
oanda_df = db.load_dataframe('oanda_ohlcv')

# Get specific instruments
eur_usd_cols = [col for col in oanda_df.columns if 'EUR_USD' in col]
eur_usd_data = oanda_df[eur_usd_cols]

# List all tables
tables = db.list_tables()
print(f"Tables: {tables}")

# Check if table exists
if db.table_exists('oanda_ohlcv'):
    print("OANDA data is available!")

# Close connection
db.close()
```

## Project Structure

```
hakuquant/
├── quantlib/               # Main package
│   ├── data.py            # Market data fetching utilities
│   ├── general_utils.py   # I/O and utility functions
│   └── database.py        # SQLite database utilities
├── brokerage/             # Brokerage integrations
│   └── oanda/            # OANDA broker implementation
├── subsystems/            # Trading subsystems
├── config/                # Configuration files
├── Data/                  # Local data storage & SQLite database
│   └── hakuquant.db      # SQLite database file
└── main.py               # Main execution script
```

## Dependencies

- pandas
- requests
- beautifulsoup4
- yfinance
- lxml
- sqlalchemy (for SQLite support)
- oandapyV20

## License

MIT
