"""Checks of the stochastic rainfall generator (sc.py gen): means, monthly CV, annual CV, dry-year quantiles, persistence. 100,000 years, seed 11."""
import numpy as np
from sc import *
P=gen(100000,seed=11)*1000
a=P.sum(1)
print("generator, seed 11, 100,000 years: annual mean %.0f mm, realised annual CV %.3f, 10th percentile %.0f mm, 5th %.0f, 1st %.0f"%(a.mean(),a.std()/a.mean(),np.percentile(a,10),np.percentile(a,5),np.percentile(a,1)))
print("monthly mean",np.round(P.mean(0),1))
print("monthly CV  ",np.round(P.std(0)/P.mean(0),2))
print("observed monthly CV (input)",CVOBS)
print("CVA %.4f ; gamma multiplier CV by month"%CVA,np.round(CVM,3))
print("lag-1 autocorr of annual totals %.3f (rho=0)"%np.corrcoef(a[:-1],a[1:])[0,1])
print("P(month rain < 5 mm):",np.round((P<5).mean(0),2))
