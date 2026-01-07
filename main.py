from quantlib import data as du
from quantlib import general_utils as gu
from quantlib.database import Database
import datetime
import json
import pandas as pd

from subsystems.lbmom.subsys import Lbmom
from dateutil.relativedelta import relativedelta
from brokerage.oanda.oanda import Oanda


# df , instruments = du.get_sp500_df()
# df = du.extend_dataframe(instruments , df)
# gu.save_file("./Data/historical_df.obj" , (df , instruments))

# df , instrumnets =gu.load_file("./Data/historical_df.obj")
#print(instrumnets)

with open("config/auth_config.json") as f:
    auth_config = json.load(f)

with open("config/oan_config.json") as f:
    brokerage_config = json.load(f)

with open("config/portfolio_config.json") as f:
    portfolio_config = json.load(f) #settings for the portfolio

brokerage = Oanda(auth_config=auth_config)


db_instruments = brokerage_config["currencies"] + brokerage_config["indices"] \
    + brokerage_config["commodities"] + brokerage_config["metals"] + brokerage_config["bonds"]


# Pull OHLCV data from OANDA for all instruments
# print(f"Fetching OHLCV data for {len(db_instruments)} instruments...")
# trade_client = brokerage.get_trade_client()

# # Dictionary to store OHLCV data for each instrument
# ohlcv_data = {}

# # Fetch data for each instrument (using 5000 candles of daily data)
# for inst in db_instruments:
#     try:
#         print(f"Fetching data for {inst}...")
#         ohlcv_df = trade_client.get_ohlcv(instrument=inst, count=5000, granularity="D")
#         if ohlcv_df is not None and not ohlcv_df.empty:
#             ohlcv_data[inst] = ohlcv_df
#             print(f"  ✓ Got {len(ohlcv_df)} candles for {inst}")
#         else:
#             print(f"  ✗ No data for {inst}")
#     except Exception as e:
#         print(f"  ✗ Error fetching {inst}: {str(e)}")

# print(f"\nSuccessfully fetched data for {len(ohlcv_data)} instruments")

# # Create combined DataFrame with consistent format: {inst} {column_name}
# # Use the first instrument's dates as the base index
# if ohlcv_data:
#     first_inst = list(ohlcv_data.keys())[0]
#     database_df = pd.DataFrame(index=ohlcv_data[first_inst]['date'])
#     database_df.index.name = 'date'
    
#     # Add data for each instrument with proper column naming
#     for inst in ohlcv_data.keys():
#         inst_df = ohlcv_data[inst].set_index('date')
        
#         # Rename columns to match format: {inst} {column_name}
#         for col in ['open', 'high', 'low', 'close', 'volume']:
#             database_df[f"{inst} {col}"] = inst_df[col]
    
#     # Forward fill any missing values
#     database_df.fillna(method='ffill', inplace=True)
#     database_df.fillna(method='bfill', inplace=True)
    
#     print(f"\nCombined DataFrame shape: {database_df.shape}")
#     print(f"Date range: {database_df.index[0]} to {database_df.index[-1]}")
    
#     # Store in SQLite database
#     print("\nStoring data in SQLite database...")
#     try:
#         # Initialize SQLite database (stored in Data/hakuquant.db)
#         db = Database(db_path='Data/hakuquant.db')
        
#         # Save the combined dataframe to SQLite
#         db.save_dataframe(database_df, table_name='oanda_ohlcv', if_exists='replace')
        
#         print("✓ Data successfully stored in SQLite database 'Data/hakuquant.db'")
        
#         # Close database connection
#         db.close()
        
#     except Exception as e:
#         print(f"✗ Error storing data in SQLite: {str(e)}")
#         print("  Fallback: You can save to Excel instead:")
#         print("  database_df.to_excel('oanda_data.xlsx')")
# else:
#     print("No data fetched. Cannot create database_df")



try:
    db = Database(db_path='./Data/hakuquant.db')
    
    # Check if table exists
    if db.table_exists('oanda_ohlcv'):
        # Load the entire OHLCV dataframe from database
        database_df = db.load_dataframe('oanda_ohlcv')
        
    #     # Extract instruments from column names
    #     instruments = list(set([col.split(' ')[0] for col in database_df.columns]))
        
    #     print(f"\n✓ Loaded data for {len(instruments)} instruments")
    #     print(f"  DataFrame shape: {database_df.shape}")
    #     print(f"  Date range: {database_df.index[0]} to {database_df.index[-1]}")
    #     print(f"\nAvailable instruments: {instruments[:10]}{'...' if len(instruments) > 10 else ''}")
        
    #     # Display sample data
    #     print(f"\nFirst few rows:")
    #     print(database_df.head())
        
    #     print(f"\nLast few rows:")
    #     print(database_df.tail())
        
    #     # Example: Get data for a specific instrument
    #     if instruments:
    #         sample_inst = instruments[0]
    #         inst_cols = [col for col in database_df.columns if col.startswith(sample_inst)]
    #         print(f"\nSample data for {sample_inst}:")
    #         print(database_df[inst_cols].tail())
        
    #     db.close()
        
    #     # Now you can perform operations on database_df
    #     # For example, extend the dataframe with additional calculations
    #     # historical_data = du.extend_dataframe(instruments, database_df)
        
    # else:
    #     print("✗ Table 'oanda_ohlcv' does not exist in database")
    #     print("  Run the data fetching section first to populate the database")
        
except Exception as e:
    print(f"✗ Error loading from database: {str(e)}")
    print("  Make sure you've run the data fetching section at least once")




historical_data = du.extend_dataframe(traded=db_instruments, df=database_df, fx_codes=brokerage_config["fx_codes"])

# print(historical_data)
# import random
# pairs = []

# while len(pairs) <= 20:
#     pair = random.sample(list(range(16, 300)),2)
#     if pair[0] == pair[1]:
#         continue
#     else:
#         pairs.append((min(pair[0],pair[1]), max(pair[0], pair[1])))
# print(pairs)


# loading from config 
vol_target = portfolio_config["vol_target"]
sim_start = datetime.date.today() - relativedelta(years=portfolio_config["sim_years"])



strat = Lbmom(
    './subsystems/lbmom/config.json', 
    historical_df=historical_data,
    simulation_start=sim_start,
    vol_target=vol_target
)

strat.get_subsys_pos()