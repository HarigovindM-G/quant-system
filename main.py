from quantlib import data as du
from quantlib import general_utils as gu 

from subsystems.lbmom.subsys import Lbmom
from dateutil.relativedelta import relativedelta

# df , instruments = du.get_sp500_df()
# df = du.extend_dataframe(instruments , df)
# gu.save_file("./Data/historical_df.obj" , (df , instruments))

df , instrumnets =gu.load_file("./Data/historical_df.obj")
#print(instrumnets)

# import random

# pairs = []

# while len(pairs) <= 20:
#     pair = random.sample(list(range(16, 300)),2)
#     if pair[0] == pair[1]:
#         continue
#     else:
#         pairs.append((min(pair[0],pair[1]), max(pair[0], pair[1])))
# print(pairs)
sim_data = df.index[-1] - relativedelta(years=5)
print(sim_data)

VOLATILITY_TARGET= 0.20

strat = Lbmom('./subsystems/lbmom/config.json' , df ,sim_data , VOLATILITY_TARGET)

strat.get_subsys_pos()