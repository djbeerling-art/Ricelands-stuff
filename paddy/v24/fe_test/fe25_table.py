import sys, numpy as np, pandas as pd, os
O='/home/user/runs/out/paddy'; K=16e-3*1e4
def integ(d,f,cols):
    p=f'{d}/flx/{f}'
    if not os.path.exists(p): return {c:np.nan for c in cols}
    x=pd.read_csv(p,sep=r'\s+'); t=np.concatenate([[0],x.time.values]); dt=np.diff(t)
    return {c: float((x[c].values*dt).sum()) if c in x else 0. for c in cols}
def row(n):
    d=f'{O}/flood_{n}'
    g=integ(d,'flx_gas-pch4.txt',['g2ch4','ch4o2','ch4rx','ch4pl','ch4eb','dif'])
    f=integ(d,'flx_aq-fe2.txt',['g2fe3','g2gt','g2gr'])
    em=(g['ch4pl']+g['ch4eb']+g['dif'])*K
    return -g['g2ch4']*K, em, g['ch4o2']*K, g['ch4rx']*K, -(f['g2fe3']+f['g2gt']+f['g2gr'])
for grp in [('ref',['fe_ref_0','fe_ref_20','fe_ref_20f6','fe_ref_20f12','fe_ref_20f25']),('gong',['fe_gong_0','fe_gong_36','fe_gong_36f6','fe_gong_36f12']),('slag',['fe_slag_0','fe_slag_4','fe_slag_4f15']),('bat',['fe_bat_0','fe_bat_20','fe_bat_20f12'])]:
    base=None
    for n in grp[1]:
        p,e,so,rx,fe=row(n)
        if base is None: base=(p,e)
        print(f'{n:14s} prod {p:7.1f} ({100*(p/base[0]-1):+5.1f}%)  emis {e:7.1f} ({100*(e/base[1]-1) if base[1] else 0:+5.1f}%)  soilox {so:6.1f} rhizox {rx:6.1f} g2fe3 {fe:7.3f}')
