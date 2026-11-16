"""SI figure: probability density functions used for the Monte-Carlo sampling (R1 line 190), drawn from the parameters in sc.py.
  (a) lognormal annual factor (mean 1, CV = CVA);  (b) gamma monthly multipliers (mean 1, CV = CVM_t, one curve per month group).
Output: ../results/figures/FigureS3_rainfall_multiplier_pdfs.png/.pdf   (python3 fig_S_mc_pdfs.py)"""
import numpy as np
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sc import CVA, CVM
NAVY,LIGHT,RED='#1f4e79','#9dc3e6','#b03a2e'
mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig,ax=plt.subplots(1,2,figsize=(9,3.4))
s=np.sqrt(np.log(1+CVA**2)); x=np.linspace(0.2,2.2,600)
ax[0].plot(x,stats.lognorm.pdf(x,s,scale=np.exp(-s**2/2)),color=NAVY,lw=2)
ax[0].axvline(1,color='0.6',lw=.8,ls=':')
ax[0].set_xlabel('Annual factor (-)',fontsize=9); ax[0].set_ylabel('Probability density',fontsize=9)
ax[0].set_title('(a) Annual factor: lognormal, mean 1, CV = %.3f'%CVA,fontsize=9)
x=np.linspace(0.001,3.5,1200)
for t in range(12):
    k=1/CVM[t]**2
    dry=t in (10,11,0,1,2,3)
    ax[1].plot(x,stats.gamma.pdf(x,k,scale=1/k),color=RED if dry else NAVY,lw=1.6 if t in (0,8) else 0.8,alpha=1 if t in (0,8) else .55)
for t,dx,dy in ((0,.06,2.6),(8,1.1,1.6)):
    k=1/CVM[t]**2; ax[1].annotate('%s (CV %.2f)'%(mon[t],CVM[t]),xy=(dx,min(stats.gamma.pdf(dx,k,scale=1/k),3.3)),xytext=(dx+.45,dy),fontsize=7.5,arrowprops=dict(arrowstyle='-',lw=.6,color='0.4'))
ax[1].set_ylim(0,3.6); ax[1].set_xlabel('Monthly multiplier (-)',fontsize=9)
ax[1].set_title('(b) Monthly multiplier: gamma, mean 1, month-specific CV\n(red: Nov-Apr, blue: May-Oct)',fontsize=9)
for a in ax:
    for sp in('top','right'): a.spines[sp].set_visible(False)
    a.tick_params(labelsize=8)
fig.tight_layout(); fig.savefig('../results/figures/FigureS3_rainfall_multiplier_pdfs.png',dpi=200); fig.savefig('../results/figures/FigureS3_rainfall_multiplier_pdfs.pdf')
# check: moments of the densities
print('lognormal mean %.3f CV %.3f'%(np.exp(-s**2/2)*np.exp(s**2/2),np.sqrt(np.exp(s**2)-1)))
print('gamma CV by month',np.round(CVM,3))
