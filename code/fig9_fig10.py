"""Figures 7 and 8 of the revised manuscript (Figs. 9 and 10 of the discussion paper): main-system storage over the year and
distribution of annual reliability, from sc.py. Designs (Table 4): mean-year dA=95,730 m2 and robust dA=188,713 m2, both dV=20,000 m3, K=117,133.
Fig. 9: month-end storage of the main system (a) in the mean year at periodic steady state (70 identical years, last year shown), robust design
        and mean-year design; (b) robust design over the Monte-Carlo sample (seed 11; 1,390 evaluated years after a 60-yr spin-up): median and 10-90 % band.
Fig. 10: annual reliability of year y = 1 - (months with import)/12, over the same 1,390 years. Nothing else is assumed."""
import numpy as np
from sc import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
K=117133.; dV=20000.; DR,DM=188713.,95730.; Vm=VMAIN0+dV
def trace(Pr,dAc,spin=60):                       # same recursion as sc.simulate (evap=0); also returns month-end main storage
    Pr=np.atleast_2d(Pr); Ir=CROOF*ETA*Pr*AROOF; Iru=K*Pr+CROOF*ETA*Pr*dAc
    St,Sm=VTANK*.5,Vm*.5; im=np.zeros((len(Pr),12)); sm=np.zeros((len(Pr),12))
    for y in range(len(Pr)):
        for t in range(12):
            at=St+Ir[y,t]; qt=min(at,DEMF[t]); nd=DEMF[t]-qt; St=min(at-qt,VTANK)
            am=Sm+Iru[y,t]; qm=min(am,nd); nd2=nd-qm; Sm=min(am-qm,Vm)
            im[y,t]=(nd2-min(GW,nd2))>1e-3; sm[y,t]=Sm
    return im[spin:],sm[spin:]
Pe=gen(1500,seed=11)[50:]; Pm=np.tile(MU,(70,1))
res={}
for nm,dA in (('robust',DR),('mean-year',DM)):
    im,sm=trace(Pe,dA); assert np.array_equal(im,simulate(Pe,dA,dV,K)), 'trace differs from sc.simulate'
    imm,smm=trace(Pm,dA,spin=69)                 # last of 70 identical mean years
    ann=1-im.sum(1)/12
    res[nm]=dict(im=im,sm=sm,smm=smm[0],immm=imm[0],ann=ann)
    print(nm,'dA',dA,'years',len(ann),'long-run rel',round(ann.mean(),3),
          '| share of years: 12/12 months ok',round((ann==1).mean(),3),'>=11/12',round((ann>=11/12-1e-9).mean(),3),
          '| mean-year import months',int(res[nm]['immm'].sum()),'| min month-end storage in mean year (m3)',round(smm[0].min()),
          '| P(main store empty at month end)',round((sm<1e-6).mean(),3))
    print('  distribution of failure months per year:',{k:round(float((im.sum(1)==k).mean()),3) for k in range(0,13) if (im.sum(1)==k).any()})
    print('  mean-year month-end storage (m3):',np.round(smm[0]).astype(int).tolist())
M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; x=np.arange(12)
# Fig 9
fig,ax=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
ax[0].plot(x,res['robust']['smm']/1e3,'o-',color='#4c72b0',label='Robust design (%s m$^2$)'%format(int(DR),','))
ax[0].plot(x,res['mean-year']['smm']/1e3,'s--',color='#dd8452',label='Mean-year design (%s m$^2$)'%format(int(DM),','))
ax[0].axhline(Vm/1e3,color='grey',lw=.8,ls=':'); ax[0].text(0,Vm/1e3+2,'capacity %s m$^3$'%format(int(Vm),','),ha='left',fontsize=8,color='grey')
ax[0].set_title('(a) Mean year (periodic steady state)',fontsize=10)
q=np.percentile(res['robust']['sm'],[10,50,90],axis=0)/1e3
ax[1].fill_between(x,q[0],q[2],color='#4c72b0',alpha=.25,label='10-90 %% of %s evaluated years'%format(len(res['robust']['ann']),',')); ax[1].plot(x,q[1],'o-',color='#4c72b0',label='Median')
ax[1].axhline(Vm/1e3,color='grey',lw=.8,ls=':'); ax[1].set_title('(b) Robust design, Monte-Carlo years',fontsize=10)
for a in ax:
    a.set_xticks(x); a.set_xticklabels(M,fontsize=8); a.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,.93))
    for s in ('top','right'): a.spines[s].set_visible(False)
ax[0].set_ylabel('Main-system storage at month end (10$^3$ m$^3$)')
plt.tight_layout(); plt.savefig('../results/figures/Figure07_reservoir_operation.png',dpi=200); plt.savefig('../results/figures/Figure07_reservoir_operation.pdf'); plt.close()
# Fig 10
fig,ax=plt.subplots(figsize=(6.5,3.8)); w=.38; ks=np.arange(0,13)
for i,(nm,c,lab) in enumerate((('mean-year','#dd8452','Mean-year design'),('robust','#4c72b0','Robust design'))):
    fr=[(res[nm]['im'].sum(1)==k).mean() for k in ks]
    ax.bar(ks+(i-.5)*w,fr,w,color=c,label='%s (long-run reliability %.2f)'%(lab,res[nm]['ann'].mean()))
ax.set_xlabel('Months with import in a year'); ax.set_ylabel('Share of simulated years'); ax.set_xticks(ks)
ax.legend(frameon=False,fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('../results/figures/Figure08_annual_reliability.png',dpi=200); plt.savefig('../results/figures/Figure08_annual_reliability.pdf')
