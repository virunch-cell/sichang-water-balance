"""Per-capita use sensitivity (R2): constant wp instead of 0.12 (Nov-Apr) / 0.10 (May-Oct) m3 per person per day.
Future (stress-test) population P_tot = 10,173; demand per month = P_tot * wp * 30 (as in sens_V.py). K = 117,133, dV = 20,000, seed 11, 1,390 evaluated years."""
from sc import *
K=117133.; Pe=gen(1500,seed=11)[50:]
roofy=CROOF*ETA*MU.sum()*AROOF; WB=K*MU.sum(); gwy=12*GW
for lab,w in (("paper 0.12/0.10",None),("constant 0.10",.10),("constant 0.11",.11),("constant 0.12",.12)):
    dem=DEMF if w is None else np.full(12,10173*w*30.)
    print("%-16s demand %7.0f  deficit %8.0f  robust catchment (0.90) %8.0f"%(lab,dem.sum(),dem.sum()-roofy-WB-gwy,mincat(Pe,20000.,K,hi=900000.,dem=dem)))
