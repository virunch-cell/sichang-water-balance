"""Figure 6 of the revised manuscript (catchment-storage trade-off; Fig. 8 of the discussion paper), computed from the model in sc.py.
Usage:
  python3 fig8_frontier.py calc 0 10000      # run the model for these added storages (m3) and append to ../results/raw_output/fig8_frontier.csv
  python3 fig8_frontier.py plot              # draw ../results/figures/Figure06_frontier.png/.pdf from the CSV only
Settings identical to run_all.py: K = 117,133, Monte-Carlo sample gen(1500, seed 11)[50:] with a 60-yr spin-up discarded (1,390 years evaluated), bisection to reliability target.
Columns: dV, robust catchment for reliability 0.85 / 0.90 / 0.95, mean-year design (smallest catchment for which every month of the mean year is satisfactory).
"""
import sys, os, csv
import numpy as np
CSVF='../results/raw_output/fig8_frontier.csv'
cmd=sys.argv[1]
if cmd=='calc':
    from sc import *
    K=117133.; Pe=gen(1500,seed=11)[50:]; Pm=np.tile(MU,(70,1))
    def detcat(dV):
        lo,hi=0.,600000.
        for _ in range(30):
            m=(lo+hi)/2
            if simulate(Pm,m,dV,K).sum()==0: hi=m   # mean-year design: no import month at periodic steady state
            else: lo=m
        return hi
    done={}
    if os.path.exists(CSVF): done={int(r['dV']):r for r in csv.DictReader(open(CSVF))}
    for dV in map(int,sys.argv[2:]):
        r=[round(mincat(Pe,float(dV),K,target=tg)) for tg in (.85,.90,.95)]
        done[dV]=dict(dV=dV,rel085=r[0],rel090=r[1],rel095=r[2],mean_year=round(detcat(float(dV))))
        print(done[dV],flush=True)
    with open(CSVF,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['dV','rel085','rel090','rel095','mean_year']); w.writeheader()
        for k in sorted(done): w.writerow(done[k])
elif cmd=='plot':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    rows=sorted(csv.DictReader(open(CSVF)),key=lambda r:int(r['dV']))
    x=np.array([int(r['dV']) for r in rows])/1000.
    g=lambda k: np.array([int(r[k]) for r in rows])/1000.
    fig,ax=plt.subplots(figsize=(6.2,4.0),dpi=300)
    ax.axvspan(20,x.max()*1.03,color='0.93',zorder=0)
    ax.plot(x,g('mean_year'),'o--',color='0.35',lw=1.6,label='Mean-year design')
    ax.plot(x,g('rel085'),'o-',color='#7fb2d9',lw=1.6,label='Robust design, reliability 0.85')
    ax.plot(x,g('rel090'),'o-',color='#1f4e79',lw=2.2,label='Robust design, reliability 0.90')
    ax.plot(x,g('rel095'),'o-',color='#0b2540',lw=1.6,label='Robust design, reliability 0.95')
    ax.axvline(20,color='#b03a2e',lw=1.4)
    ax.text(20.8,ax.get_ylim()[1]*0.97,'Built tank\n(20,000 m$^3$)',color='#b03a2e',fontsize=8,va='top')
    ax.text(x.max()*0.99,ax.get_ylim()[1]*0.60,'Hypothetical additional storage',fontsize=7.5,color='0.35',ha='right',style='italic')
    ax.set_xlabel('Added storage $\\Delta V$ (10$^3$ m$^3$)',fontsize=9); ax.set_ylabel('Additional catchment $\\Delta A_{cat}$ (10$^3$ m$^2$)',fontsize=9)
    ax.set_xlim(-2,x.max()*1.03); ax.set_ylim(bottom=0); ax.tick_params(labelsize=8)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.legend(fontsize=7.5,frameon=False,loc='upper right',bbox_to_anchor=(1.0,0.97))
    fig.tight_layout(); fig.savefig('../results/figures/Figure06_frontier.png'); fig.savefig('../results/figures/Figure06_frontier.pdf'); print('plot ok')
