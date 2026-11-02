import glob,re,sys,numpy as np,pandas as pd
O='/home/user/runs/out/paddy/'
def alk_top(run,y,tdrain=99/365):
    fs=glob.glob(O+f'flood_{run}_y{y}s/prof/prof_aq(tot)-*.txt')
    best=None
    for f in fs:
        x=pd.read_csv(f,sep=r'\s+'); t=x.time.iloc[0]
        if best is None or abs(t-tdrain)<abs(best[0]-tdrain): best=(t,x)
    t,x=best; r=x.iloc[0]
    alk=2*r.ca+2*r.mg+r.na+r.k+2*r.fe2-2*r.so4-r.no3-r.cl   # eq/L (Al/Fe3 ignored)
    return t,alk*1e3,r.get('aph',np.nan)  # meq/L
res={}
for run in sys.argv[1:]:
    res[run]=[alk_top(run,y) for y in range(1,11)]
    print(run,' '.join(f'{a:.2f}' for t,a,p in res[run]),' t=%.3f'%res[run][0][0])
c,tr=sys.argv[1],sys.argv[2]
irr=0.2
for h in (0.05,0.10):
  for f in (0.3,1.0):
    d=sum((f*a2+(1-f)*irr)-(f*a1+(1-f)*irr) for (_,a1,_),(_,a2,_) in zip(res[c],res[tr]))*h  # meq/L*m = eq/m2
    print(f'h={h*1000:.0f}mm f={f}: extra ALK export 10 yr = {d:.2f} eq/m2 = {d*0.44:.2f} t CO2/ha')
