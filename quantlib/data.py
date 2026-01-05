import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
import datetime


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    res = requests.get(url, headers=headers)
    res.raise_for_status()  # good practice

    soup = BeautifulSoup(res.content, "lxml")

    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(str(table))[0]

    return df["Symbol"].tolist()

#print(symbols)

def get_sp500_df():   
    symbols = get_sp500_tickers()
    symbols = symbols[:30]
    ohlcvs = {}
    for symbol in symbols:
        symbol_df = yf.Ticker(symbol).history(period = "10y")
        ohlcvs[symbol] = symbol_df[["Open","High","Low","Close","Volume"]].rename(
            columns = {
                "Open" : "open",
                "High" : "high",
                "Low": "low",
                "Close" : "close",
                "Volume" : "volume",
            }
        )
    
    df = pd.DataFrame(index=ohlcvs["MMM"].index)
    df.index.name = "date"
    instruments = list(ohlcvs.keys())

    for inst in instruments:
        inst_df = ohlcvs[inst]
        columns = list(map(lambda x: "{} {}".format(inst , x), inst_df.columns))
        df[columns] = inst_df
    
    return df , instruments

def extend_dataframe(traded , df):
    df.index = pd.to_datetime(df.index).date
    # so what we are doing here is that we are slicing only the part that we need to trade on and then calculating stuff based on that
    # the param 'traded' contains a list of instruments that we are using at the momement
    open_cols = list(map(lambda x : str(x) + " open" , traded))
    high_cols = list(map(lambda x : str(x) + " high" , traded))
    low_cols = list(map(lambda x : str(x) + " low" , traded))
    close_cols = list(map(lambda x : str(x) + " close" , traded))
    volume_cols = list(map(lambda x: str(x) + " volume", traded))
    historical_df = df.copy()
    historical_df = historical_df[open_cols + high_cols + low_cols + close_cols + volume_cols] 
    historical_df.fillna(method="ffill" , inplace = True)

    # we have to make 2 new colums that % return and volatility
    # % return = (close of today / close of yesterday ) - 1
    # % volatility  = rolling std of % over 25 days 
    for inst in traded:
        historical_df["{} %ret".format(inst)] =  historical_df["{} close".format(inst)] / historical_df["{} close".format(inst)].shift(1) - 1
        historical_df["{} %ret vol".format(inst)] = historical_df["{} %ret".format(inst)].rolling(25).std()
        historical_df["{} active".format(inst)] = historical_df["{} close".format(inst)] != historical_df["{} close".format(inst)].shift(1)
    historical_df.fillna(method="bfill" , inplace = True)
    #historical_df.index = historical_df.index.tz_localize(None)
    return historical_df

if __name__ == "__main__":
    df , instruments = get_sp500_df()
    #df.index = df.index.tz_localize(None)
    #df.to_excel("sp500_data.xlsx")
    historical_data = extend_dataframe(["MMM","AOS","ACN"], df)
    historical_data.to_excel("hist.xlsx")
