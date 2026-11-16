"""Which calendar months have a failure month (import needed after groundwater)? Uses sc.simulate only; nothing assumed.
Samples: gen(1500, seed 11)[50:] with the first 60 years discarded by simulate (1,390 evaluated years), as in the paper; and the mean year."""
import numpy as np
from sc import *
K=117133.
DEMC=np.array(col('03_demand_monthly.csv','demand_current_m3'))
M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
Pe=gen(1500,seed=11)[50:]; Pm=np.tile(MU,(70,1))
def rep(name,Pr,dA,dV,dem):
    im=simulate(Pr,dA,dV,K,dem=dem); f=im.mean(0)   # share of years with failure in each calendar month
    tot=im.sum(); dry=im[:,[10,11,0,1,2,3]].sum()
    print(f'{name}: years {im.shape[0]}, failure months per year {im.sum(1).mean():.2f}, share of failure months in Nov-Apr {dry/tot if tot else float("nan"):.3f}')
    print('   share of years with failure, by month:',' '.join(f'{M[i]} {f[i]:.2f}' for i in range(12)))
rep('present system, current demand, generated rain',Pe,0,0,DEMC)
rep('present system, stress-test demand, generated rain',Pe,0,0,DEMF)
rep('robust design 188,713 m2 + 20,000 m3, generated rain',Pe,188713.,20000.,DEMF)
rep('mean-year design 95,730 m2 + 20,000 m3, generated rain',Pe,95730.,20000.,DEMF)
rep('present system, current demand, mean year',Pm,0,0,DEMC)
rep('present system, stress-test demand, mean year',Pm,0,0,DEMF)
