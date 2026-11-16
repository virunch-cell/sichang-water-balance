import numpy as np, csv
def col(fn,c): return [float(r[c]) for r in csv.DictReader(open(fn))]
MU=np.array(col('01_rainfall_observed_monthly.csv','rainfall_mm'))/1000.
WRES=np.array(col('02_watershed_runoff_monthly.csv','Wres_m3'))
DEMF=np.array(col('03_demand_monthly.csv','demand_future_m3'))
# open-water evaporation = mean Class A pan (Chon Buri, Phatthaya; TMD 2023) x pan coefficient 0.80 (Rittima et al. 2013); file 04 (old literature-based profile, 1,348 mm/yr) is no longer used
ETmm=np.array(col('04b_evaporation_pan_TMD_monthly.csv','open_water_evaporation_mm'))
MUp=np.array(col('05_rcp45_projected_monthly.csv','rainfall_mm'))/1000.
K_OLD=(WRES/MU).mean()
CROOF,ETA,AROOF,ARES=0.85,0.9,245000.,34335.
VTANK,VMAIN0,GW=5650.,116144.,1440.
# Variability of the stochastic generator (month-specific, from the observed Ko Sichang record 1985-2025; file 10_rainfall_cv_monthly.csv)
CVOBS=np.array(col('10_rainfall_cv_monthly.csv','cv_monthly_1985_2025'))   # observed CV of monthly rainfall
CVA=0.1342   # CV of the annual factor, calibrated (calibrate_cva.py) so that the realised annual CV equals the observed 0.231
CVM=np.sqrt((1+CVOBS**2)/(1+CVA**2)-1)   # CV of the independent monthly gamma multiplier
TMULT=np.array([1.3,1.2,1.0,1.5,0.8,0.7,0.75,0.85,0.7,0.8,1.15,1.25])
def simulate(Pr,dAc,dV,K,dem=DEMF,evap=0,roof=AROOF,gw=GW,spin=60):
    Pr=np.atleast_2d(Pr); Vm=VMAIN0+dV; Ir=CROOF*ETA*Pr*roof; Iru=K*Pr+CROOF*ETA*Pr*dAc
    St,Sm=VTANK*.5,Vm*.5; im=np.zeros((Pr.shape[0],12))
    for y in range(Pr.shape[0]):
        for t in range(12):
            at=St+Ir[y,t]; qt=min(at,dem[t]); nd=dem[t]-qt; St=min(at-qt,VTANK)
            am=Sm+Iru[y,t]
            if evap:
                A=ARES*(am/Vm) if evap==1 else ARES
                am=max(0.,am-max(0.,A*ETmm[t]/1000.))
            qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm); im[y,t]=(nd2-min(gw,nd2))>1e-3
    return im[spin:] if Pr.shape[0]>spin else im
def rel(Pr,dAc,dV,K,**kw):
    im=simulate(Pr,dAc,dV,K,**kw); return 1-im.sum()/(im.shape[0]*12)
def gen(n,seed=11,mu=MU,rho=0.,cva=CVA):
    rng=np.random.default_rng(seed); s=np.sqrt(np.log(1+cva**2)); k=1/CVM**2
    z=rng.standard_normal(n); la=np.zeros(n); la[0]=z[0]*s
    for y in range(1,n): la[y]=rho*la[y-1]+np.sqrt(1-rho**2)*s*z[y]
    kap=np.exp(la-s**2/2); return np.array([mu*kap[y]*rng.gamma(k,1/k,12) for y in range(n)])
def mincat(Pe,dV,K,target=0.9,lo=0.,hi=600000.,it=24,**kw):
    for _ in range(it):
        m=(lo+hi)/2
        if rel(Pe,m,dV,K,**kw)>=target: hi=m
        else: lo=m
    return (lo+hi)/2
