import sys, numpy as np
from sc import *
K=117133.
WB=K*MU
FR=0.5539+2*0.4261+5*0.0201   # 1.5066 d
RES=4522
WP=np.array([.12,.12,.12,.12,.10,.10,.10,.10,.10,.10,.12,.12])
def rnd(x): return int(np.floor(x+0.5))
def demand(V,lab):
    emv=rnd(V*FR/360); lb=rnd(lab*emv); ptot=RES+emv+lb
    return ptot*WP*30, emv, lb, ptot
Pe=gen(1500,seed=11)[50:]
roofy=CROOF*ETA*MU.sum()*AROOF
def mean_year(dem,years=80,dA=0.):
    Vm=VMAIN0; St,Sm=VTANK*.5,Vm*.5; Ir=CROOF*ETA*MU*AROOF; Iru=WB+CROOF*ETA*MU*dA
    for y in range(years):
        defs=[]
        for t in range(12):
            at=St+Ir[t]; qt=min(at,dem[t]); nd=dem[t]-qt; St=min(at-qt,VTANK)
            am=Sm+Iru[t]; qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm)
            defs.append(max(0.,nd2-min(GW,nd2)))
    d=np.array(defs); return round(d.sum()/1500,1), int((d>1e-3).sum())
rows=[("V","lab")]
sc=[(600000,.5),(700000,.5),(800000,.5),(900000,.5),(900000,0),(900000,.25),(900000,1.0),(600000,0),(600000,1.0)]
print("V lab emv labour Ptot demand deficit | meanyear_import_days fail_months | robust_catchment(0.90,dV=20k) | rel_at_baseline_design_188713",flush=True)
for V,lab in sc:
    dem,emv,lb,pt=demand(V,lab)
    deficit=dem.sum()-roofy-WB.sum()-12*GW
    iy,fm=mean_year(dem)
    A=mincat(Pe,20000.,K,dem=dem,hi=900000.)
    r=rel(Pe,188713.,20000.,K,dem=dem)
    print(V,lab,emv,lb,pt,round(dem.sum()),round(deficit),"|",iy,fm,"|",round(A),"|",round(r,3),flush=True)
