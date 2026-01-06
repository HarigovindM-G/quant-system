# TradeClient is kinda  a think api adapter layer , it is the api layer that the strategy supports 
# so when a new brokerage comes , you can just create Zerodha trade client , cause the api is the same

from datetime import datetime
import json
import datetime 
import pandas as pd

import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.instruments as instruments


class TradeClient():

    def __init__(self, auth_config):
        #init connection
        self.id = auth_config["oan_acc_id"]
        self.token = auth_config["oan_token"]
        self.env = auth_config["oan_env"]
        self.client = oandapyV20.API(access_token=self.token, environment=self.env)

    def get_account_details(self):
        try:
            return self.client.request(accounts.AccountDetails(accountID=self.id))["account"]
        except Exception as err:
            pass

    def get_account_instruments(self):
        try:
            r = self.client.request(accounts.AccountInstruments(accountID=self.id))["instruments"]
            instruments = {}
            currencies, cfds, metals = [], [], [] #fx, index cds + commodities + bonds, metals
            for inst in r:
                inst_name = inst["name"]
                type = inst["type"]
                instruments[inst_name] = {
                    "type": type, #....other things
                }
                if type == "CFD":
                    cfds.append(inst_name)
                elif type == "CURRENCY":
                    currencies.append(inst_name)
                elif type == "METAL":
                    metals.append(inst_name)
                else:
                    print("unknown type")
                
            return instruments, currencies, cfds, metals
        except Exception as err:
            print(err)


    def get_account_summary(self):
        try:
            return self.client.request(accounts.AccountSummary(accountID=self.id))
        except Exception as err:
            raise Exception("some err message from acc summary: {}".format(str(err)))

    def get_account_capital(self):
        #we can use the summary function to get capital, since dict contains alot of useful info
        try:
            return float(self.get_account_summary()["NAV"])
        except Exception as err:
            pass

    def get_account_positions(self):
        positions_data = self.get_account_details()["positions"]
        positions = {}
        for entry in positions_data:
            instrument = entry["instrument"]
            long_pos = int(entry["long"]["units"])
            short_pos = int(entry["short"]["units"])
            net_pos = long_pos + short_pos 
            if net_pos != 0:
                positions[instrument] = net_pos
        return positions

    def get_account_trades(self):
        try:
            results = self.client.request(trades.OpenTrades(accountID=self.id))
            print(results)
        except Exception as err:
            print(err)

    def is_tradable(self, inst):
        try:
            params = {"instruments": inst}
            r = pricing.PricingInfo(accountID=self.id, params=params)
            res = self.client.request(r)
            is_tradable = res["prices"][0]["tradeable"]
            return is_tradable       
        except Exception as err:
            print(err)

    def get_endpoint(self, inst):
        pass


    def format_date(self, series):
        ddmmyy = series.split("T")[0].split("-")
        return datetime.date(int(ddmmyy[0]), int(ddmmyy[1]), int(ddmmyy[2]))
    
    def get_ohlcv(self, instrument, count, granularity):
        try:
            params = {"count": count, "granularity": granularity}
            candles = instruments.InstrumentsCandles(instrument=instrument, params=params)
            self.client.request(candles)
            ohlc_dict = candles.response["candles"]
            ohlc = pd.DataFrame(ohlc_dict)
            #lets expand the ohlc data in mid, and only take complete entries
            ohlc = ohlc[ohlc["complete"]]
            ohlc_df = ohlc["mid"].dropna().apply(pd.Series)
            ohlc_df["volume"]= ohlc["volume"]
            ohlc_df.index = ohlc["time"]
            ohlc_df = ohlc_df.apply(pd.to_numeric)
            ohlc_df.reset_index(inplace=True)
            ohlc_df.columns = ["date", "open", "high", "low", "close", "volume"]
            ohlc_df["date"] = ohlc_df["date"].apply(lambda x: self.format_date(x))
            return ohlc_df   
        except Exception as err:
            print(err)

    def market_order(self, inst, order_config={}):
        pass
        #implement later


