#!/usr/bin/env python3
"""Final v25b summary per site and dose (main set and Fig. 6b), cumulative over the years completed (10 when done).
Year-round sums (season + fallow) from paddy/ghg_budget.py per year; GWP100 (CH4 27, N2O 273).
  net realised (PDA)       = cum dCH4 + cum dN2O - [cumPDA + min(cumCalcite, max(cumCatRel - cumPDA, 0))]
  net realised (carb. ALK) = the same with carbonate ALK export in place of PDA
  net potential            = cum dCH4 + cum dN2O - cumCatRel
Exported alkalinity split (basalt minus control, carbonate ALK, t CO2/ha): lateral floodwater discharge and
percolation through the column base (= total - lateral), per year and cumulative.
Usage: python3 final_v25b.py [--years]   (--years adds the per-year lateral/base rows)
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'paddy', 'ghg_budget.py')).read().split('ctrl = season(args[0])')[0]
src = src.replace('np.loadtxt(f,skiprows=1)', 'np.loadtxt(f,skiprows=1,ndmin=2)')
peryear = '--years' in sys.argv
sys.argv = ['ghg_budget.py']
ns = {}
exec(src, ns)
B = os.path.expanduser('~/fastdata/v25_out/paddy')

def phase(run, days):
    ns['tend'] = days/365.
    return ns['season'](run)

def done(chain, y):
    for ph, tend in (('s', 0.3095), ('f', 0.6895)):
        f = f'{chain}_y{y}{ph}/flx/flx_gas-pch4.txt'
        if not os.path.exists(f):
            return False
        lines = [l for l in open(f).read().split('\n')[1:] if l.strip()]
        if not lines or float(lines[-1].split()[0]) < tend:
            return False
    return True

def year(chain, y):
    s = phase(f'{chain}_y{y}s', 113.); f = phase(f'{chain}_y{y}f', 252.)
    a = {k: s[k] + f[k] for k in s}
    a['CH4s'] = s['CH4 (kg/ha)']
    return a

print('site   set   dose yrs ctlCH4_y1 ctlCH4_yN drift%/yr dCH4%_y1 dCH4%_yN net_real_PDA net_real_ALK net_pot cum_latALK cum_baseALK cum_dcalcite cum_catrel')
for site, sets in (('ref', ('v25bb', 'v25bbw0', 'v25bbw04')), ('refq1', ('v25bb',)), ('rf189', ('v25bb',)),
                   ('irr061', ('v25bb',)), ('irr043', ('v25bb',)), ('rf184', ('v25bb',)), ('irr092', ('v25bb',)),
                   ('rf151', ('v25bb',))):
    for pre in sets:
        for d in (['10', '20'] if site in ('ref', 'refq1') else ['20']):
            ctl, trt = f'{B}/flood_{pre}_{site}_0', f'{B}/flood_{pre}_{site}_{d}'
            ny = 0
            while ny < 10 and done(ctl, ny + 1) and done(trt, ny + 1):
                ny += 1
            if ny == 0:
                print(f'{site:6s} {pre:9s} {d:>3}   0'); continue
            cum = dict(ch4=0., n2o=0., pda=0., alk=0., lat=0., cc=0., cat=0.)
            ch, yrs = [], []
            for y in range(1, ny + 1):
                c, t = year(ctl, y), year(trt, y)
                cum['ch4'] += (t['CH4 (kg/ha)'] - c['CH4 (kg/ha)'])/1e3*27
                cum['n2o'] += (t['N2O (kg N/ha)'] - c['N2O (kg N/ha)'])*44.01/28.01/1e3*273
                pk = 'potentially durable ALK (t CO2/ha)'
                cum['pda'] += t[pk] - c[pk]
                alk = t['ALK export (t CO2/ha)'] - c['ALK export (t CO2/ha)']
                lat = t['lateral ALK (t CO2/ha)'] - c['lateral ALK (t CO2/ha)']
                cum['alk'] += alk; cum['lat'] += lat
                cum['cc'] += t['calcite (t CO2/ha)'] - c['calcite (t CO2/ha)']
                cum['cat'] += t['cation release (t CO2/ha)']
                ch.append((c['CH4s'], t['CH4s'])); yrs.append((y, lat, alk - lat))
            g = cum['ch4'] + cum['n2o']
            rp = g - (cum['pda'] + min(cum['cc'], max(cum['cat'] - cum['pda'], 0.)))
            ra = g - (cum['alk'] + min(cum['cc'], max(cum['cat'] - cum['alk'], 0.)))
            pot = g - cum['cat']
            (c1, t1), (cn, tn) = ch[0], ch[-1]
            drift = 100*((cn/c1)**(1/(ny - 1)) - 1) if ny > 1 else float('nan')
            print(f'{site:6s} {pre:9s} {d:>3} {ny:3d} {c1:9.1f} {cn:9.1f} {drift:9.2f} {100*(t1/c1-1):8.1f} {100*(tn/cn-1):8.1f} '
                  f'{rp:12.2f} {ra:12.2f} {pot:7.2f} {cum["lat"]:10.3f} {cum["alk"]-cum["lat"]:11.3f} {cum["cc"]:11.3f} {cum["cat"]:9.2f}')
            if peryear:
                print('      per-year lateral/base ALK: ' + ' '.join(f'y{y}:{l:.3f}/{b:.3f}' for y, l, b in yrs))
