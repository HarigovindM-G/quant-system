from quantlib.database import Database
from quantlib import data as du
import json
import datetime
from dateutil.relativedelta import relativedelta

# Load config
with open("config/oan_config.json") as f:
    brokerage_config = json.load(f)

with open("config/portfolio_config.json") as f:
    portfolio_config = json.load(f)

# Load data from database
db = Database('Data/hakuquant.db')
database_df = db.load_dataframe('oanda_ohlcv')
db.close()

print("Before extend_dataframe:")
print(f"Index type: {type(database_df.index[0])}")
print(f"First index: {database_df.index[0]}")
print(f"Columns sample: {database_df.columns[:3].tolist()}")

# Get instruments list
db_instruments = brokerage_config["currencies"] + brokerage_config["indices"] \
    + brokerage_config["commodities"] + brokerage_config["metals"] + brokerage_config["bonds"]

# Extend dataframe
historical_data = du.extend_dataframe(traded=db_instruments, df=database_df, fx_codes=brokerage_config["fx_codes"])

print("\nAfter extend_dataframe:")
print(f"Index type: {type(historical_data.index[0])}")
print(f"First index: {historical_data.index[0]}")
print(f"Columns sample: {historical_data.columns[:5].tolist()}")
print(f"Shape: {historical_data.shape}")

# Test accessing data
test_date = historical_data.index[0]
test_inst = db_instruments[0]
print(f"\nTest access for {test_inst} on {test_date}:")
print(f"Close price: {historical_data.loc[test_date, f'{test_inst} close']}")

# Check simulation start date
sim_start = datetime.date.today() - relativedelta(years=portfolio_config["sim_years"])
print(f"\nSimulation start: {sim_start}, type: {type(sim_start)}")
print(f"Is sim_start in index? {sim_start in historical_data.index}")
print(f"Index range: {historical_data.index[0]} to {historical_data.index[-1]}")
