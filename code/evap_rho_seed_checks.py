# Checks added 2026-11-08 (R2 comments): evaporation from TMD pan data, AR(1) persistence, seed variability, RCP4.5.
# Reads 04b_evaporation_pan_TMD_monthly.csv (new) and the existing sc.py inputs. Does not modify any existing file.
# Source of pan data: TMD (2023) Climatological Data of Thailand 1991-2020, Report 551.586-13-2023, pp. 58 (Chon Buri), 60 (Phatthaya).
import numpy as np, sc
from sc import *
K=117133.0; DV=20000.; DROB=188713.
Pe=gen(1500,seed=11)[50:]
pan=np.array(col('04b_evaporation_pan_TMD_monthly.csv','pan_mean_mm'))
R=(DEMF.sum()-122040)/12; TT=DEMF-R; DEMS=R+TT*TMULT
print("== A. open-water evaporation = mean pan x Kp; robust design",DROB)
for kp in (0.60,0.70,0.80,0.85):
    sc.ETmm=pan*kp
    print("Kp %.2f annual %.0f mm | rel level %.3f / const %.3f | with seasonal tourism level %.3f / const %.3f | catch0.90 level %.0f, level+seasonal %.0f"%(
      kp,sc.ETmm.sum(),rel(Pe,DROB,DV,K,evap=1),rel(Pe,DROB,DV,K,evap=2),rel(Pe,DROB,DV,K,evap=1,dem=DEMS),rel(Pe,DROB,DV,K,evap=2,dem=DEMS),
      mincat(Pe,DV,K,evap=1,hi=900000.),mincat(Pe,DV,K,evap=1,dem=DEMS,hi=900000.)))
sc.ETmm=pan*0.8
Vm=VMAIN0+DV; Iru=K*Pe+CROOF*ETA*Pe*DROB; Ir=CROOF*ETA*Pe*AROOF; St,Sm=VTANK*.5,Vm*.5; loss=0.; n=0
for y in range(Pe.shape[0]):
    for t in range(12):
        at=St+Ir[y,t]; qt=min(at,DEMF[t]); nd=DEMF[t]-qt; St=min(at-qt,VTANK); am=Sm+Iru[y,t]
        l=min(am,max(0.,ARES*(am/Vm)*sc.ETmm[t]/1000.)); am-=l; qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm)
        if y>=60: loss+=l
    if y>=60: n+=1
print("mean annual evaporation loss (Kp 0.80, level-dependent): %.0f m3/yr"%(loss/n))
print("== B. AR(1) persistence of log annual multiplier (robust catchment @0.90)")
for r in (0,0.25,0.5,0.7): print("rho",r,round(mincat(gen(1500,seed=11,rho=r)[50:],DV,K)))
print("== C. seeds (robust catchment @0.90)")
v=[mincat(gen(1500,seed=s)[50:],DV,K) for s in (11,21,31,41,51,61)]
print([round(x) for x in v],"mean",round(np.mean(v)),"sd",round(np.std(v,ddof=1)))
print("== D. RCP4.5 (file 05 monthly climatology, single GCM)")
Pp=gen(1500,seed=11,mu=MUp)[50:]
print("robust catchment hist %.0f ; RCP4.5 %.0f"%(mincat(Pe,DV,K),mincat(Pp,DV,K)))
print("reliability of %.0f design: hist %.3f ; RCP4.5 %.3f"%(DROB,rel(Pe,DROB,DV,K),rel(Pp,DROB,DV,K)))
print("reliability of mean-year design 95,730: hist %.3f ; RCP4.5 %.3f"%(rel(Pe,95730,DV,K),rel(Pp,95730,DV,K)))
