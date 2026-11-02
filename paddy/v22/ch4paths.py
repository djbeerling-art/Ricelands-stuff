# CH4 pathway diagnostics for Si-feedback structure comparisons (O2 release vs plant conductance): per year, season
# and fallow summed, for each chain: production, soil oxidation (ch4o2), rhizosphere oxidation of plant-transported CH4
# (ch4rx), emission by plant transport (ch4pl), ebullition (ch4eb) and floodwater/surface diffusion (dif), all in
# kg CH4/ha; plus Fe(II) reoxidation by O2 (fe2o2) and root O2 release (rtoxy) in mol/m2. Sign convention: positive =
# CH4 removed from the soil gas pool (as in the flx files, where production is negative).
# Usage: python3 ch4paths.py <outdir> <nyears> <chain> [<chain> ...]   e.g. ch4paths.py out/paddy 10 r23_ref_0 r23_ref_20
import sys, os, numpy as np, pandas as pd
O, NY, CH = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
K = 16e-3*1e4   # mol/m2 -> kg CH4/ha
def integ(d, f, cols):
    x = pd.read_csv(f'{d}/flx/{f}', sep=r'\s+'); t = np.concatenate([[0], x.time.values]); dt = np.diff(t)
    return {c: float((x[c].values*dt).sum()) if c in x else 0. for c in cols}
def year(n, y):
    tot = None
    for ph in 'sf':
        d = f'{O}/flood_{n}_y{y}{ph}'
        if not os.path.isdir(f'{d}/flx'): return None
        g = integ(d, 'flx_gas-pch4.txt', ['g2ch4', 'ch4o2', 'ch4rx', 'ch4pl', 'ch4eb', 'dif'])
        fe = integ(d, 'flx_aq-fe2.txt', ['fe2o2']); o2 = integ(d, 'flx_gas-po2.txt', ['rtoxy'])
        r = np.array([-g['g2ch4']*K, g['ch4o2']*K, g['ch4rx']*K, g['ch4pl']*K, g['ch4eb']*K, g['dif']*K,
                      fe['fe2o2'], -o2['rtoxy']])
        tot = r if tot is None else tot + r
    return tot
hdr = ['prod', 'soil_ox', 'rhizo_ox', 'plant_em', 'ebull', 'diffus', 'emission', 'fe2o2', 'rtO2']
print('chain'.ljust(16) + 'yr ' + ''.join(h.rjust(9) for h in hdr))
for n in CH:
    for y in range(1, NY + 1):
        r = year(n, y)
        if r is None: break
        e = r[3] + r[4] + r[5]
        v = list(r[:6]) + [e] + list(r[6:])
        print(n.ljust(16) + f'{y:2d} ' + ''.join(f'{x:9.1f}' if i < 7 else f'{x:9.2f}' for i, x in enumerate(v)))
