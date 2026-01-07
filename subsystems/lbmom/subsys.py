"""
[(96, 164), (128, 136), (97, 135), (246, 292), (157, 175), (36, 42), (62, 103), (270, 273), (100, 292), (45, 147),
 (184, 273), (242, 294), (45, 145), (50, 91), (16, 220), (98, 274), (113, 182), (156, 207), (73, 250), (124, 155), (60, 235)]
"""
import json
from quantlib import  indicators_calc as ic
from quantlib import backtest_util
import pandas as pd 
import numpy as np

class Lbmom():

    def __init__(self, instrument_config , historical_df , simulation_start , vol_target):
        self.pairs = [(96, 164), (128, 136), (97, 135), (246, 292), (157, 175), (36, 42), (62, 103), (270, 273), (100, 292), (45, 147), (184, 273), (242, 294), (45, 145), (50, 91), (16, 220), (98, 274), (113, 182), (156, 207), (73, 250), (124, 155), (60, 235)]
        self.historical_df = historical_df 
        self.instrument_config = instrument_config
        self.simulation_start = simulation_start
        self.vol_target = vol_target
        with open(instrument_config) as f:
            self.instrument_config = json.load(f)
        self.sysname = "LBMOM"
        pass

    def extend_historicals(self , instruments , historical_data):
        # so what this function does is that it takes in the baseket of instruments and then adds neccesary columns to the df and returns the df 
        # lets just first have an arbitarty 14 period adx , this is to see weather the market is trending or not to avoid false signal from ma

        for inst in instruments:
            historical_data["{} adx".format(inst)] = ic.adx_series(
                high = historical_data["{} high".format(inst)],
                low = historical_data["{} low".format(inst)] ,
                close = historical_data["{} close".format(inst)],
                n = 14
            )
            # next we have to find fast-slow ema instead of storing both
            for pair in self.pairs:
                historical_data["{} ema{}".format(inst , str(pair))] = ic.ema_series(
                    series = historical_data["{} close".format(inst)],
                    n = pair[0] 
                ) -  ic.ema_series(
                    series=historical_data["{} close".format(inst)],
                    n= pair[1]
                ) #fastEMA - slowEMA

        return historical_data

    def run_simulation(self , historical_data):
        #init params
        instruments = self.instrument_config["indices"] + self.instrument_config["bonds"]
        
        #calculate/preprocess indicators
        historical_data = self.extend_historicals(instruments= instruments , historical_data= historical_data)

        #perform simulation
        portfolio_df = pd.DataFrame(index = historical_data[self.simulation_start:].index).reset_index()
        portfolio_df.loc[0, "capital"] = 1000
        
        is_halted = lambda inst, date: not np.isnan( historical_data.loc[date, "{} active".format(inst)]) and  (~historical_data[:date].tail(5)["{} active".format(inst)]).all()

        for i in portfolio_df.index:
            date = portfolio_df.loc[i, "index"]
            strat_scalar = 2

            tradable = [inst for inst in instruments if not is_halted(inst, date)]
            non_tradable = [inst for inst in instruments if inst not in tradable]


            """
            Get P&L and Scalar 
            """
            if i != 0:
                date_prev = portfolio_df.loc[i - 1, "index"]
                pnl = backtest_util.get_backtest_day_stats(\
                    portfolio_df, instruments, date, date_prev, i, historical_data)
                strat_scalar = backtest_util.get_strat_scaler(\
                    portfolio_df, 100, self.vol_target, i, strat_scalar)
            
            portfolio_df.loc[i, "strat scalar"] = strat_scalar
            


            """
            Get Positions for Traded Instruments, Assign 0 to Non-Traded
            """

            for inst in non_tradable:
                portfolio_df.loc[i , "{} units".format(inst)] = 0
                portfolio_df.loc[i , "{} w".format(inst)] = 0

            
            nominal_total = 0
            for inst in tradable:
                # here we are just calculating how much moving averages crossed which is the signal for the strategy 
                votes = self.calulate_vote(historical_data= historical_data , inst= inst , date= date) 
                # we are trying to find the strength of the strategy here . if every pairs cross super bullish , signal is 1 
                forecast = votes / len(self.pairs)

                # even though we are relying on the signal , before we reley on it completly we look at the adx 
                # to see if there is a real trend in any direction , just to make sure its not noise
                forecast = 0 if historical_data.loc[date , "{} adx".format(inst)] < 25 else forecast

                # this kinda gives the dollar amount which is riskable for 1 asset in the profolio right 
                position_vol_target = (1/len(tradable)) * portfolio_df.loc[i ,"capital"] * self.vol_target/np.sqrt(253)

                #current price
                inst_price = historical_data.loc[date, "{} close".format(inst)]
                
                percent_ret_vol = historical_data.loc[date, "{} %ret vol".format(inst)] if historical_data[:date].tail(25)["{} active".format(inst)].all() else 0.025
                
                # this tell you , according to past volatility how much will the stock change in a day in dollars 
                dollar_volatility = inst_price * percent_ret_vol

                # so now you kinda get how much to buy (just from asset vol targetting)  = position_vol_target/ dollar_volatilty target 
                # this is like saying your wiggle budget for the day is 600 , then you have 2 assets, so for 1 is 300
                #asset 1 wiggles 100 a day , so i can hold 3 units , that is the logic behind it 
                position = strat_scalar * forecast * position_vol_target / dollar_volatility
                portfolio_df.loc[i, "{} units".format(inst)] = position

                # this is the gross exposure we are talking about 
                nominal_total += abs(position * inst_price)

            for inst in tradable:
                units = portfolio_df.loc[i, "{} units".format(inst)]
                nominal_inst = abs(units * historical_data.loc[date, "{} close".format(inst)])
                # calculates the weight of the asset in the portfolio 
                inst_w = nominal_inst / nominal_total
                portfolio_df.loc[i, "{} w".format(inst)] = inst_w

            
            #logging 
            portfolio_df.loc[i, "nominal"] = nominal_total

            #leverage will be there cause the nominal exposure can go beyond the capital due to volatility targetting
            # so leverage is nominal_exposure / captial , how much asset do we control for 1 dollar of our own capital .
            portfolio_df.loc[i, "leverage"] = portfolio_df.loc[i, "nominal"] / portfolio_df.loc[i, "capital"]
            
            print(portfolio_df.loc[i]) 

        print(portfolio_df)

        portfolio_df.to_excel("see.xlsx") 
        
        return portfolio_df

    def get_subsys_pos(self):
        self.run_simulation(historical_data=self.historical_df)

    def calulate_vote(self, historical_data, inst , date):
        vote = 0
        for pair in self.pairs:
            if(historical_data.loc[date , "{} ema{}".format(inst , str(pair))] > 0):
                vote += 1 
        return vote