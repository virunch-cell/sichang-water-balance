"""Effect of eta = 0.90 instead of 0.80 on the main results (everything else as in run_all.py). Usage: python3 eta_check.py 0.8|0.9"""
import sys, sc, numpy as np
from sc import *
sc.ETA=float(sys.argv[1]); ETA=sc.ETA; K=117133.
dem_cur=np.array([float(r['demand_current_m3']) for r in csv.DictReader(open('03_demand_monthly.csv'))])
def mean_year(dem,years=80):
    St,Sm=VTANK*.5,VMAIN0*.5; Ir=CROOF*ETA*MU*AROOF; Irun=K*MU
    for y in range(years):
        used=spill=0.; d=[]
        for t in range(12):
            at=St+Ir[t]; qt=min(at,dem[t]); nd=dem[t]-qt; spill+=max(0,at-qt-VTANK); St=min(at-qt,VTANK); used+=qt
            am=Sm+Irun[t]; qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,VMAIN0); d.append(max(0.,nd2-min(GW,nd2)))
    d=np.array(d); f=d>1e-3; nf=int(f.sum()); ok=sum(1 for t in range(12) if f[t] and not f[(t+1)%12])
    return dict(used=round(used),spill=round(spill),imp_days=round(d.sum()/1500,1),rel=round(1-nf/12,2),res=None if nf==0 else round(ok/nf,2),vul=round(d[f].mean()) if nf else 0)
print('eta',ETA,'C*eta',CROOF*ETA)
roof=CROOF*ETA*MU.sum()*AROOF; print('rooftop potential',round(roof),'deficit',round(DEMF.sum()-roof-K*MU.sum()-12*GW))
print('T6 cur',mean_year(dem_cur)); print('T6 fut',mean_year(DEMF))
Pe=gen(1500,seed=11)[50:]; Pm=np.tile(MU,(70,1))
def detcat(dV):
    lo,hi=0.,600000.
    for _ in range(30):
        m=(lo+hi)/2
        if simulate(Pm,m,dV,K).sum()==0: hi=m   # mean-year design: no import month at periodic steady state
        else: lo=m
    return hi
for dV in (0.,20000.,40000.):
    dm=detcat(dV); rb=mincat(Pe,dV,K)
    print('dV',int(dV),'mean-year',round(dm),'rel of it',round(rel(Pe,dm,dV,K),3),'| robust 0.90',round(rb),'ratio',round(rb/dm,2),flush=True)
