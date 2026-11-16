"""CV of rainfall from the daily record of the Ko Sichang station (TMD, 1985-2025), and a sensitivity run of the robust design.
Input: ../../459202-*.csv (Date, Rainfall mm/day; 41 years, no missing days).  Output: ../results/raw_output/cv_from_daily.txt
Run: python3 cv_from_daily.py
"""
import glob, io, contextlib, numpy as np, pandas as pd
from sc import *
out=io.StringIO()
def P(*a): print(*a,file=out); print(*a)
f=glob.glob('../data_raw/459202*.csv')[0]
d=pd.read_csv(f,encoding='utf-8-sig',parse_dates=['Date']); d['y']=d.Date.dt.year; d['m']=d.Date.dt.month
A=d.groupby('y').Rainfall.sum(); M=d.groupby(['y','m']).Rainfall.sum().unstack()
P("days",len(d),"years",len(A),d.Date.min().date(),d.Date.max().date(),"missing values",int(d.Rainfall.isna().sum()))
for lab,s in (("1985-2025",A),("2012-2021",A.loc[2012:2021])): P("annual",lab,"mean %.1f SD %.1f CV %.3f min %.0f max %.0f"%(s.mean(),s.std(ddof=1),s.std(ddof=1)/s.mean(),s.min(),s.max()))
P("annual lag-1 / lag-2 autocorrelation (41 y): %.2f / %.2f"%(A.autocorr(1),A.autocorr(2)))
P("monthly means 1985-2025:",M.mean().round(1).tolist()); P("monthly means 2012-2021:",M.loc[2012:2021].mean().round(1).tolist()); P("model MU (mm):",(MU*1000).round(1).tolist())
raw=(M.std(ddof=1)/M.mean()).values; P("observed monthly CV by month:",raw.round(2).tolist())
G=gen(100000,seed=11)*1000; P("generator (CVa 0.20, CVm 0.35): monthly CV",(G.std(0)/G.mean(0)).round(2).tolist(),"annual CV",round(G.sum(1).std()/G.sum(1).mean(),3))
K=117133.; cva=0.2; cvm=np.sqrt((1+raw**2)/(1+cva**2)-1)
def gen2(n,seed=11):
    rng=np.random.default_rng(seed); s=np.sqrt(np.log(1+cva**2)); kap=np.exp(rng.standard_normal(n)*s-s**2/2); k=1/cvm**2
    return np.array([MU*kap[y]*rng.gamma(k,1/k) for y in range(n)])
G2=gen2(100000); P("month-specific gamma CV:",cvm.round(2).tolist(),"-> monthly CV",(G2.std(0)/G2.mean(0)).round(2).tolist(),"annual CV",round(G2.sum(1).std()/G2.sum(1).mean(),3))
Pe=gen2(1500)[50:]; P("SENSITIVITY month-specific CV: robust catchment",round(mincat(Pe,20000.,K)),"(baseline 148226); reliability of 148,226 design",round(rel(Pe,148226.,20000,K),3))
open('../results/raw_output/cv_from_daily.txt','w').write(out.getvalue())
