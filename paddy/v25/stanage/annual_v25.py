#!/usr/bin/env python3
"""Year-round (season + fallow) budgets of v25 chains against their matched control, per year.
Uses the per-run accounting of paddy/ghg_budget.py (CH4, N2O, ALK export incl. floodwater lateral ALK, potentially
durable ALK, calcite, cation release), summed over the season (0.31 yr) and the fallow (0.69 yr) of each year.
Net realised year-round (t CO2e/ha, GWP100: CH4 27, N2O 273) = dCH4 + dN2O - [dALK + min(dcalcite, max(cation release - dALK, 0))],
the same calcite cap as ghg_budget.py but on annual sums. Season CH4 is reported separately.
Usage: python3 annual_v25.py <paddy dir> <chain prefix, e.g. v25bb> <site> <dose> [<dose> ...]
"""
import sys, os
import numpy as np

P, pre, site = sys.argv[1], sys.argv[2], sys.argv[3]
doses = sys.argv[4:]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'paddy', 'ghg_budget.py')).read()
src = src.split('ctrl = season(args[0])')[0]
sys.argv = ['ghg_budget.py']
ns = {}
exec(src, ns)

def phase(run, days):
    ns['tend'] = days/365.
    return ns['season'](run)

def year(chain, y):
    s = phase(f'{P}/flood_{chain}_y{y}s', 113.)
    f = phase(f'{P}/flood_{chain}_y{y}f', 252.)
    a = {k: s[k] + f[k] for k in s}
    a['CH4 season (kg/ha)'] = s['CH4 (kg/ha)']
    return a

def done(chain, y):
    # a year counts only when both phases have run to their end time (a running phase has a partial flux file)
    for ph, tend in (('s', 0.3095), ('f', 0.6895)):
        f = f'{P}/flood_{chain}_y{y}{ph}/flx/flx_gas-pch4.txt'
        if not os.path.exists(f):
            return False
        lines = [l for l in open(f).read().split('\n')[1:] if l.strip()]
        if not lines or float(lines[-1].split()[0]) < tend:
            return False
    return True

ctl = f'{pre}_{site}_0'
print(f'{site} ({pre})  per year: season CH4 control/treatment kg/ha, %; year-round t CO2/ha: cation release, ALK export '
      f'(incl. lateral), lateral ALK, PDA, calcite; net realised year-round t CO2e/ha')
print('dose yr  CH4ctl  CH4trt   dCH4%  catrel  ALKexp  latALK     PDA  calcite  net_yr')
for d in doses:
    if d == '0':
        continue
    trt = f'{pre}_{site}_{d}'
    for y in range(1, 11):
        if not (done(ctl, y) and done(trt, y)):
            break
        c, t = year(ctl, y), year(trt, y)
        dch4 = (t['CH4 (kg/ha)'] - c['CH4 (kg/ha)'])/1e3*27
        dn2o = (t['N2O (kg N/ha)'] - c['N2O (kg N/ha)'])*44.01/28.01/1e3*273
        dalk = t['ALK export (t CO2/ha)'] - c['ALK export (t CO2/ha)']
        dcc = t['calcite (t CO2/ha)'] - c['calcite (t CO2/ha)']
        cdr = dalk + min(dcc, max(t['cation release (t CO2/ha)'] - dalk, 0.))
        cs, ts = c['CH4 season (kg/ha)'], t['CH4 season (kg/ha)']
        print(f'{d:>4} {y:2d} {cs:7.1f} {ts:7.1f} {100*(ts/cs-1):7.1f} {t["cation release (t CO2/ha)"]:7.3f} '
              f'{dalk:7.3f} {t["lateral ALK (t CO2/ha)"]-c["lateral ALK (t CO2/ha)"]:7.3f} '
              f'{t["potentially durable ALK (t CO2/ha)"]-c["potentially durable ALK (t CO2/ha)"]:7.3f} {dcc:8.3f} {dch4+dn2o-cdr:7.3f}')
