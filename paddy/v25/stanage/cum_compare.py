#!/usr/bin/env python3
"""v23 vs v25b side by side, same accounting: year-round (season + fallow) sums per year from paddy/ghg_budget.py,
PDA as the alkalinity term, GWP100 (CH4 27, N2O 273), calcite capped cumulatively:
  cumulative CDR(n) = cumPDA(n) + min(cumCalcite(n), max(cumCationRelease(n) - cumPDA(n), 0))
  net realised (n)  = cum dCH4 + cum dN2O - cumulative CDR(n);  net potential (n) = cum dCH4 + cum dN2O - cumCationRelease(n)
Control CH4 drift: geometric mean %/yr of season CH4 from year 1 to the last year done.
Usage: python3 cum_compare.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'paddy', 'ghg_budget.py')).read().split('ctrl = season(args[0])')[0]
src = src.replace('np.loadtxt(f,skiprows=1)', 'np.loadtxt(f,skiprows=1,ndmin=2)')   # single-record flux files
sys.argv = ['ghg_budget.py']
ns = {}
exec(src, ns)
A = os.path.expanduser('~/fastdata/alt_out/paddy')
B = os.path.expanduser('~/fastdata/v25_out/paddy')

def phase(run, days):
    ns['tend'] = days/365.
    return ns['season'](run)

def done(chain, y):
    # a year counts only if both phases ran to their end time (a failed run can leave an empty flux file)
    for ph, tend in (('s', 0.3095), ('f', 0.6895)):
        f = f'{chain}_y{y}{ph}/flx/flx_gas-pch4.txt'
        if not os.path.exists(f):
            return False
        lines = open(f).read().split('\n')[1:]
        lines = [l for l in lines if l.strip()]
        if not lines or float(lines[-1].split()[0]) < tend:
            return False
    return True

def year(chain, y):
    s = phase(f'{chain}_y{y}s', 113.); f = phase(f'{chain}_y{y}f', 252.)
    a = {k: s[k] + f[k] for k in s}
    a['CH4s'] = s['CH4 (kg/ha)']
    return a

def run(ctl, trt):
    ny = 0
    while ny < 10 and done(ctl, ny + 1) and done(trt, ny + 1):
        ny += 1
    if ny == 0:
        return None
    cum = dict(ch4=0., n2o=0., pda=0., cc=0., cat=0.)
    rows = []
    for y in range(1, ny + 1):
        c, t = year(ctl, y), year(trt, y)
        cum['ch4'] += (t['CH4 (kg/ha)'] - c['CH4 (kg/ha)'])/1e3*27
        cum['n2o'] += (t['N2O (kg N/ha)'] - c['N2O (kg N/ha)'])*44.01/28.01/1e3*273
        pk = 'potentially durable ALK (t CO2/ha)'
        cum['pda'] += t[pk] - c[pk]
        cum['cc'] += t['calcite (t CO2/ha)'] - c['calcite (t CO2/ha)']
        cum['cat'] += t['cation release (t CO2/ha)']
        rows.append((c['CH4s'], t['CH4s']))
    cdr = cum['pda'] + min(cum['cc'], max(cum['cat'] - cum['pda'], 0.))
    real = cum['ch4'] + cum['n2o'] - cdr
    pot = cum['ch4'] + cum['n2o'] - cum['cat']
    c1, t1 = rows[0]; cn, tn = rows[-1]
    drift = 100*((cn/c1)**(1/(ny - 1)) - 1) if ny > 1 else np.nan
    return ny, c1, cn, 100*(t1/c1 - 1), 100*(tn/cn - 1), real, pot, drift

print('site    dose ver   yrs  ctlCH4_y1 ctlCH4_yN  dCH4%_y1 dCH4%_yN  net_real  net_pot  ctl_drift%/yr')
for s in ['ref', 'rf189', 'irr061', 'irr043', 'rf184', 'irr092', 'rf151']:
    for d in (['10', '20'] if s == 'ref' else ['20']):
        for ver, ctl, trt in (('v23 ', f'{A}/flood_a_{s}_o2_0', f'{A}/flood_a_{s}_o2_{d}'),
                              ('v25b', f'{B}/flood_v25bb_{s}_0', f'{B}/flood_v25bb_{s}_{d}')):
            r = run(ctl, trt)
            if r is None:
                print(f'{s:7s} {d:>4} {ver}   0  (no completed years)')
                continue
            ny, c1, cn, p1, pn, real, pot, drift = r
            print(f'{s:7s} {d:>4} {ver} {ny:3d} {c1:10.1f} {cn:9.1f} {p1:9.1f} {pn:8.1f} {real:9.2f} {pot:8.2f} {drift:10.2f}')
