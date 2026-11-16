"""Figures 11 and 12 computed from the model in sc.py (same settings as run_all.py: K = 117,133, dV = 20,000 m3, Monte-Carlo sample of 1,390 evaluated years, seed 11).
  python3 fig11_fig12.py calc11 <parameter> ...   # robust catchment (m2, reliability 0.90) at -20/-10/+10/+20 %, appended to ../results/raw_output/fig11_sensitivity.csv
        parameters: "Per-capita use" "Tourism demand" "Roof area" "Runoff coefficient" "Groundwater yield" ; the structural deficit (panel a) is analytic and is written with the first call
  python3 fig11_fig12.py calc12                   # reliability of the 188,713 m2 design under evaporation / seasonal tourism, monthly evaporation loss -> ../results/raw_output/fig12_*.csv
  python3 fig11_fig12.py plot                     # draw ../results/figures/Figure09_sensitivity.png/.pdf and ../results/figures/Figure10_evaporation_tourism.png/.pdf from the CSV files only
"""
import sys, os, csv
import numpy as np
RAW='../results/raw_output/'
P_NAMES=("Per-capita use","Tourism demand","Roof area","Runoff coefficient","Groundwater yield")
STEPS=(-.2,-.1,.1,.2)
def wcsv(fn,rows,fields):
    with open(RAW+fn,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow(r) for r in rows]
def rcsv(fn): return list(csv.DictReader(open(RAW+fn)))
cmd=sys.argv[1]
if cmd in('calc11','calc12'):
    from sc import *
    K=117133.; Pe=gen(1500,seed=11)[50:]
    R=(DEMF.sum()-122040)/12; TT=DEMF-R; DEMS=R+TT*TMULT
if cmd=='calc11':
    fn='fig11_sensitivity.csv'; done=[r for r in rcsv(fn)] if os.path.exists(RAW+fn) else []
    done={r['parameter']:r for r in done}
    WB=K*MU; roofy=CROOF*ETA*MU.sum()*AROOF
    for nm in map(str,sys.argv[2:]):
        row={'parameter':nm}
        for p in STEPS:
            dm=DEMF.sum();ro=roofy;wb=WB.sum();gw=12*GW; kw={}; Kk=K
            if nm=="Per-capita use": dm*=1+p; kw['dem']=DEMF*(1+p)
            elif nm=="Roof area": ro*=1+p; kw['roof']=AROOF*(1+p)
            elif nm=="Runoff coefficient": wb*=1+p; Kk=K*(1+p)
            elif nm=="Tourism demand": dm+=122040*p; kw['dem']=DEMF*(1+p*122040/DEMF.sum())
            else: gw*=1+p; kw['gw']=GW*(1+p)
            row['deficit_%+d'%round(p*100)]=round(dm-ro-wb-gw)
            row['robust_%+d'%round(p*100)]=round(mincat(Pe,20000.,Kk,hi=900000.,**kw))
        done[nm]=row; print(row,flush=True)
    base=round(DEMF.sum()-roofy-WB.sum()-12*GW)
    fields=['parameter']+['deficit_%+d'%round(p*100) for p in STEPS]+['robust_%+d'%round(p*100) for p in STEPS]
    wcsv(fn,[done[k] for k in P_NAMES if k in done],fields)
    open(RAW+'fig11_baseline.txt','w').write("baseline structural deficit %d\nbaseline robust catchment %d\n"%(base,round(mincat(Pe,20000.,K))))
elif cmd=='calc12':
    dA=mincat(Pe,20000.,K)
    rows=[]
    for nm,ev in (("none",0),("level",1),("const",2)):
        rows.append({'evaporation':nm,'uniform':round(rel(Pe,dA,20000,K,evap=ev),3),'seasonal':round(rel(Pe,dA,20000,K,evap=ev,dem=DEMS),3)})
    wcsv('fig12_reliability.csv',rows,['evaporation','uniform','seasonal']); print(rows)
    # monthly evaporation loss (level-dependent area) at the design, mean over the post-spin-up years
    Vm=VMAIN0+20000.; Ir=CROOF*ETA*Pe*AROOF; Iru=K*Pe+CROOF*ETA*Pe*dA
    St,Sm=VTANK*.5,Vm*.5; loss=np.zeros((Pe.shape[0],12))
    for y in range(Pe.shape[0]):
        for t in range(12):
            at=St+Ir[y,t]; qt=min(at,DEMF[t]); nd=DEMF[t]-qt; St=min(at-qt,VTANK)
            am=Sm+Iru[y,t]; A=ARES*(am/Vm); am2=max(0.,am-max(0.,A*ETmm[t]/1000.)); loss[y,t]=am-am2
            qm=min(am2,nd); nd2=nd-qm; Sm=min(am2-qm,Vm)
    L=loss[60-50:].mean(0)   # Pe starts at year 50 of the generated record; discard 60 years of spin-up in total
    mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    wcsv('fig12_monthly.csv',[{'month':mon[t],'evap_loss_m3':round(L[t]),'pan_evap_mm':round(ETmm[t],1),'tourism_multiplier':TMULT[t]} for t in range(12)],['month','evap_loss_m3','pan_evap_mm','tourism_multiplier'])
    print("annual loss",round(L.sum()),"design",round(dA))
elif cmd=='plot':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    NAVY,LIGHT,RED='#1f4e79','#9dc3e6','#b03a2e'
    def clean(a):
        for s in('top','right'): a.spines[s].set_visible(False)
        a.tick_params(labelsize=8)
    # ---- Figure 11
    rows={r['parameter']:r for r in rcsv('fig11_sensitivity.csv')}
    base=dict(l.split(' ',2)[1:] and (l.rsplit(' ',1)[0],float(l.rsplit(' ',1)[1])) for l in open(RAW+'fig11_baseline.txt').read().strip().split('\n'))
    b_def=base['baseline structural deficit']; b_rob=base['baseline robust catchment']
    fig,ax=plt.subplots(1,2,figsize=(8.2,3.4),dpi=300)
    for a,(key,b,ttl,unit) in zip(ax,(('deficit',b_def,'(a) Structural annual deficit','10$^3$ m$^3$ yr$^{-1}$'),('robust',b_rob,'(b) Drought-robust catchment','10$^3$ m$^2$'))):
        order=sorted(rows,key=lambda n:-(abs(float(rows[n][key+'_+20'])-float(rows[n][key+'_-20']))))
        y=np.arange(len(order))[::-1]
        for yy,n in zip(y,order):
            r=rows[n]
            for lo,hi,col,h in (('-20','+20',LIGHT,.62),('-10','+10',NAVY,.34)):
                v1,v2=float(r[key+'_'+lo])/1000.,float(r[key+'_'+hi])/1000.
                a.barh(yy,abs(v2-v1),left=min(v1,v2),height=h,color=col,zorder=2)
        a.axvline(b/1000.,color=RED,ls='--',lw=1.2,zorder=3)
        a.set_yticks(y); a.set_yticklabels(order if a is ax[0] else ['']*len(order),fontsize=8)
        a.set_title(ttl,fontsize=9,loc='left'); a.set_xlabel(unit,fontsize=8.5); clean(a); a.grid(axis='x',color='0.9',zorder=0)
    from matplotlib.patches import Patch
    ax[1].legend(handles=[Patch(color=NAVY,label='$\\pm$10 %'),Patch(color=LIGHT,label='$\\pm$20 %'),plt.Line2D([],[],color=RED,ls='--',label='Baseline')],fontsize=7.5,frameon=False,loc='lower right')
    fig.tight_layout(); fig.savefig('../results/figures/Figure09_sensitivity.png'); fig.savefig('../results/figures/Figure09_sensitivity.pdf'); plt.close(fig)
    # ---- Figure 12
    rel=rcsv('fig12_reliability.csv'); mon=rcsv('fig12_monthly.csv')
    fig,ax=plt.subplots(1,2,figsize=(8.2,3.4),dpi=300,gridspec_kw={'width_ratios':[1,1.25]})
    lab={'none':'No\nevaporation','level':'Level-dependent\nsurface','const':'Constant\nsurface'}
    x=np.arange(len(rel)); w=.36
    b1=ax[0].bar(x-w/2,[float(r['uniform']) for r in rel],w,color=NAVY,label='Uniform tourism',zorder=2)
    b2=ax[0].bar(x+w/2,[float(r['seasonal']) for r in rel],w,color=LIGHT,label='Seasonal (peak) tourism',zorder=2)
    for bars in (b1,b2):
        for b in bars: ax[0].text(b.get_x()+b.get_width()/2,b.get_height()+.004,'%.2f'%b.get_height(),ha='center',fontsize=7.5)
    ax[0].axhline(.9,color=RED,ls='--',lw=1.2,zorder=3); ax[0].text(len(rel)-.42,.903,'Target 0.90',color=RED,fontsize=7.5,ha='right',va='bottom')
    ax[0].set_xticks(x); ax[0].set_xticklabels([lab[r['evaporation']] for r in rel],fontsize=8)
    ax[0].set_ylim(.7,.985); ax[0].set_ylabel('Long-run reliability (-)',fontsize=8.5); ax[0].set_title('(a) Reliability of the robust design',fontsize=9,loc='left'); ax[0].legend(fontsize=7.5,frameon=False,loc='upper left',bbox_to_anchor=(0,1.0),ncol=1); clean(ax[0])
    m=[r['month'] for r in mon]; xm=np.arange(12)
    ax[1].bar(xm,[float(r['evap_loss_m3'])/1000. for r in mon],color=NAVY,zorder=2,label='Evaporation loss')
    ax[1].set_xticks(xm); ax[1].set_xticklabels(m,fontsize=8); ax[1].set_ylabel('Evaporation loss (10$^3$ m$^3$ month$^{-1}$)',fontsize=8.5)
    ax[1].set_title('(b) Monthly evaporation loss and tourism multiplier',fontsize=9,loc='left'); clean(ax[1])
    a2=ax[1].twinx(); a2.plot(xm,[float(r['tourism_multiplier']) for r in mon],'o-',color=RED,lw=1.6,ms=4,label='Tourism multiplier'); a2.set_ylabel('Seasonal tourism multiplier (-)',fontsize=8.5,color=RED); a2.tick_params(labelsize=8,colors=RED); a2.spines['top'].set_visible(False); a2.set_ylim(0,2.3); ax[1].set_ylim(0,4.6)
    h1,l1=ax[1].get_legend_handles_labels(); h2,l2=a2.get_legend_handles_labels(); ax[1].legend(h1+h2,l1+l2,fontsize=7.5,frameon=False,loc='upper left',ncol=2)
    fig.tight_layout(); fig.savefig('../results/figures/Figure10_evaporation_tourism.png'); fig.savefig('../results/figures/Figure10_evaporation_tourism.pdf'); print('plots ok')
