import sys, json
from sc import *
lab=sys.argv[1]; K=K_OLD if lab=='old' else 117133.
REST=len(sys.argv)>2 and sys.argv[2]=='rest'   # 'rest': resume at the last Fig. 8 row (dV=80,000); used to split the run into <3-minute chunks
QUIET=REST
if lab=='oldp': K=140020/MU.sum()
out={}
def P(*a,**k):
    if not QUIET: print(*a,flush=True)
R=(DEMF.sum()-122040)/12; TT=DEMF-R; DEMS=R+TT*TMULT
dem_cur=np.array([float(r['demand_current_m3']) for r in csv.DictReader(open('03_demand_monthly.csv'))])
def imp_days(Pe,dAc,dV,K,**kw):
    Pe=np.atleast_2d(Pe); Vm=VMAIN0+dV; dem=kw.get('dem',DEMF); evap=kw.get('evap',0)
    Ir=CROOF*ETA*Pe*AROOF; Iru=K*Pe+CROOF*ETA*Pe*dAc; St,Sm=VTANK*.5,Vm*.5; tot=0.;n=0
    for y in range(Pe.shape[0]):
        for t in range(12):
            at=St+Ir[y,t]; qt=min(at,dem[t]); nd=dem[t]-qt; St=min(at-qt,VTANK); am=Sm+Iru[y,t]
            qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm)
            if y>=60-0: tot+=max(0.,nd2-min(GW,nd2))
    return tot/(Pe.shape[0]-60)/1500
def mean_year(Irun_m,dem,years=80):
    Vm=VMAIN0; St,Sm=VTANK*.5,Vm*.5; Ir=CROOF*ETA*MU*AROOF
    for y in range(years):
        used=spill=0.; defs=[]
        for t in range(12):
            at=St+Ir[t]; qt=min(at,dem[t]); nd=dem[t]-qt; spill+=max(0,at-qt-VTANK); St=min(at-qt,VTANK); used+=qt
            am=Sm+Irun_m[t]; qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm)
            defs.append(max(0.,nd2-min(GW,nd2)))
    defs=np.array(defs); fail=defs>1e-3; nf=int(fail.sum())
    ok=sum(1 for t in range(12) if fail[t] and not fail[(t+1)%12])
    return dict(used=round(used),spill=round(spill),inflow=round(Irun_m.sum()),imp_days=round(defs.sum()/1500,1),rel=round(1-nf/12,2),res=None if nf==0 else round(ok/nf,2),vul=round(defs[fail].mean()) if nf else 0)
P("K",round(K),"inflow",round(K*MU.sum()))
WB=K*MU
P("T6 cur",mean_year(WB,dem_cur)); P("T6 fut",mean_year(WB,DEMF))
roofy=CROOF*ETA*MU.sum()*AROOF
P("4.1 rooftop",round(roofy),"inflow",round(WB.sum()),"sum",round(roofy+WB.sum()+12*GW),"deficit",round(DEMF.sum()-roofy-WB.sum()-12*GW))
Pe=gen(1500,seed=11)[50:]
Pm=np.tile(MU,(70,1))
def detcat(dV,K):
    lo,hi=0.,600000.
    for _ in range(30):
        m=(lo+hi)/2
        if simulate(Pm,m,dV,K).sum()==0: hi=m   # mean-year design: no import month at periodic steady state
        else: lo=m
    return hi
dA_det=detcat(20000,K); dA_rob=mincat(Pe,20000,K)
P("T7 det",round(dA_det),"rel",round(rel(Pe,dA_det,20000,K),3),"imp d",round(imp_days(Pe,dA_det,20000,K),1))
P("T7 rob",round(dA_rob),"rel",round(rel(Pe,dA_rob,20000,K),3),"imp d",round(imp_days(Pe,dA_rob,20000,K),1))
P("det dV=0:",round(detcat(0,K)))
P("T8 (design robust):")
for N in (100,250,500,1000,1390,2000,3000,5000):   # 1,390 = length of the design runs
    Pn=gen(N+50,seed=100+N)[50:]; im=simulate(Pn,dA_rob,20000,K,spin=0); ann=1-im.sum(1)/12
    P("  ",N,round(1-im.sum()/im.size,3),round(1.96*ann.std(ddof=1)/np.sqrt(len(ann)),3))
QUIET=False
if not REST: P("Fig8 frontier:")
for dV in ((80000,) if REST else (0,10000,20000,40000,80000)):
    r=[round(mincat(Pe,float(dV),K,target=tg)) for tg in (.85,.90,.95)]
    P("  dV",dV,r,"evap",round(mincat(Pe,float(dV),K,evap=1)),"det",round(detcat(dV,K)),flush=True)
P("T9 deficit (analytic):")
base=DEMF.sum()-roofy-WB.sum()-12*GW; P(" base",round(base))
for nm in ("Per-capita use","Roof area","Runoff coefficient","Tourism demand","Groundwater yield"):
    row=[]
    for p in (-.2,-.1,.1,.2):
        dm=DEMF.sum();ro=roofy;wb=WB.sum();gw=12*GW
        if nm=="Per-capita use": dm*=1+p
        elif nm=="Roof area": ro*=1+p
        elif nm=="Runoff coefficient": wb*=1+p
        elif nm=="Tourism demand": dm+=122040*p
        else: gw*=1+p
        row.append(round(dm-ro-wb-gw))
    P(" ",nm,row)
P("T10 robust catchment (baseline seed11):",round(dA_rob))
Pe2=Pe
for nm in ("Per-capita use","Tourism demand","Roof area","Runoff coefficient","Groundwater yield"):
    row=[]
    for p in (-.2,-.1,.1,.2):
        kw={}; Kk=K
        if nm=="Per-capita use": kw['dem']=DEMF*(1+p)
        elif nm=="Tourism demand": kw['dem']=DEMF*(1+p*122040/DEMF.sum())   # tourism base 122,040 m3/yr = 30.29% of future demand; monthly demand scaled in proportion
        elif nm=="Roof area": kw['roof']=AROOF*(1+p)
        elif nm=="Runoff coefficient": Kk=K*(1+p)
        else: kw['gw']=GW*(1+p)
        row.append(round(mincat(Pe2,20000.,Kk,hi=900000.,**kw)))
    P(" ",nm,row,flush=True)
P("T11 (design=%d):"%round(dA_rob))
for nm,ev in (("none",0),("level",1),("const",2)):
    P(" ",nm,"uniform",round(rel(Pe,dA_rob,20000,K,evap=ev),3),"seasonal",round(rel(Pe,dA_rob,20000,K,evap=ev,dem=DEMS),3),flush=True)
P(" catchment for 0.90 level-evap + seasonal:",round(mincat(Pe,20000.,K,evap=1,dem=DEMS,hi=900000.)))
P("extras: RCP4.5",round(mincat(gen(1500,seed=11,mu=MUp)[50:],20000,K)),"rho.5",round(mincat(gen(1500,seed=11,rho=.5)[50:],20000,K)),"CV.30",round(mincat(gen(1500,seed=11,cva=.3)[50:],20000,K)),"evap",round(mincat(Pe,20000,K,evap=1)))
P("DONE")
