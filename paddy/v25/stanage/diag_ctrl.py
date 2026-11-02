#!/usr/bin/env python3
"""Per-year control diagnosis for v25 chains: season CH4 emission and production (kg CH4/ha), and end-of-year
(fallow end) inventories in the plough layer 0-0.2 m and the whole column (mol/m2) of amfe3, gt, gr, g2, cc.
Usage: python3 diag_ctrl.py <paddy dir> <chain name> [years]
"""
import sys, os, glob
import numpy as np, pandas as pd

P, name = sys.argv[1], sys.argv[2]
ny = int(sys.argv[3]) if len(sys.argv) > 3 else 10
KG = 16.04e-3 * 1e4

def season(run):
    f = f'{run}/flx/flx_gas-pch4.txt'
    h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
    dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
    c = lambda k: float((d[:, h.index(k)]*dt).sum())*KG if k in h else 0.0
    return c('dif') + c('ch4eb') + c('ch4pl'), -c('g2ch4')

def read_sld(f):
    # header: 'z' then 5-character species names run together (e.g. 'amfe3sid'), then 'time'
    h = open(f).readline().rstrip('\n')
    d = np.loadtxt(f, skiprows=1, ndmin=2)
    tok = h.split()
    if len(tok) == d.shape[1]:   # profile records: names separated by spaces
        return pd.DataFrame(d, columns=tok)
    body = h.split('z', 1)[1].rstrip()
    if body.endswith('time'):
        body = body[:-4]
    body = body[1:] if body.startswith(' ') else body
    names = [body[i:i + 5].strip() for i in range(0, len(body), 5)]
    names = [n for n in names if n]
    d = np.loadtxt(f, skiprows=1, ndmin=2)
    return pd.DataFrame(d[:, :len(names) + 1], columns=['z'] + names)

def inv(run):
    f = f'{run}/prof/prof_sld-save.txt'
    if not os.path.exists(f):
        # pruned runs keep the profile records: the last one is the end state
        rec = sorted(glob.glob(f'{run}/prof/prof_sld-[0-9][0-9][0-9].txt'))
        if not rec:
            return None
        f = rec[-1]
    d = read_sld(f)
    z = d['z'].values; dz = np.gradient(z)
    pl = z < 0.2
    out = {}
    for k in ('amfe3', 'gt', 'gr', 'g2', 'cc'):
        v = d[k].values if k in d else np.zeros(len(z))
        out[k] = (float(np.sum(v[pl]*dz[pl])), float(np.sum(v*dz)))
    return out

def dinv(run):
    # change in plough-layer and column inventory over one run from zint_sld-<m> (tflx per depth, time-integrated;
    # solid-phase tflx is the storage change rate)
    # column only (flx_sld tflx, rate per record, integrated over time); the plough-layer share is not resolved per
    # year, so the plough column carries nan until the end-state check
    out = {}
    for k in ('amfe3', 'gt', 'gr', 'g2', 'cc'):
        f = f'{run}/flx/flx_sld-{k}.txt'
        if not os.path.exists(f):
            out[k] = (np.nan, 0.0); continue
        h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
        dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
        out[k] = (np.nan, float(np.sum(d[:, h.index('tflx')]*dt)))   # solid tflx = inventory change rate (checked against the end state)
    return out

start = inv(f'{P}/flood_{name}_st')
print(f'{name}: inventories mol/m2 as plough(0-0.2 m)/column')
print('yr  CH4emis  CH4prod   amfe3        gt           gr           g2           cc')
def row(y, e, p, iv):
    s = ' '.join(f'{iv[k][0]:6.1f}/{iv[k][1]:<6.1f}' for k in ('amfe3', 'gt', 'gr', 'g2', 'cc')) if iv else 'n/a'
    print(f'{y:>3} {e:8.1f} {p:8.1f}  {s}')
row('st', np.nan, np.nan, start)
cur = {k: list(v) for k, v in start.items()} if start else None
for y in range(1, ny + 1):
    s = f'{P}/flood_{name}_y{y}s'
    if not os.path.exists(f'{s}/flx/flx_gas-pch4.txt'):
        break
    e, p = season(s)
    if cur:
        for r in (s, f'{P}/flood_{name}_y{y}f'):
            for k, (a, b) in dinv(r).items():
                cur[k][0] += a; cur[k][1] += b
    meas = inv(f'{P}/flood_{name}_y{y}f')   # measured end-of-year state when the fallow profiles were kept
    row(y, e, p, meas if meas else ({k: tuple(v) for k, v in cur.items()} if cur else None))
end = inv(f'{P}/flood_{name}_y{ny}f')
if end:
    row('end', np.nan, np.nan, end)   # check: should match the accumulated year-10 row
