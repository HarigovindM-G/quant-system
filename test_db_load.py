from quantlib.database import Database
import pandas as pd

# Load data
db = Database('Data/hakuquant.db')
df = db.load_dataframe('oanda_ohlcv')

print("Index type:", type(df.index[0]))
print("First few index values:")
print(df.index[:5])
print("\nDataFrame info:")
print(df.info())
print("\nFirst row:")
print(df.iloc[0])
print("\nColumn names (first 10):")
print(df.columns[:10].tolist())

# Check if we can access by date
import datetime
test_date = df.index[0]
print(f"\nTest date: {test_date}, type: {type(test_date)}")

# Try to convert to date
df.index = pd.to_datetime(df.index).date
print(f"\nAfter conversion, first index: {df.index[0]}, type: {type(df.index[0])}")

# Try to access a column
first_col = df.columns[0]
print(f"\nFirst column: {first_col}")
print(f"Can access by loc: {df.loc[df.index[0], first_col]}")

db.close()
