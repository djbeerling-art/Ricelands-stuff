#!/usr/bin/env python3
"""Export the v25b production results (Stanage, ~/fastdata/v25_out) as small CSV/JSON files for figure regeneration.
Writes to paddy/v25/results/:
  ghg_phase_rows.csv        per chain, year and phase (season/fallow): the per-run quantities of paddy/ghg_budget.py
  timeline_ref{10,20}.json  per year, treatment minus year-matched control, year-round: cat (cation release), pda, alk,
                            lat (floodwater lateral ALK), cc (calcite), dch4/dn2o (t CO2e/ha) - the keys fig7_ref_fate reads
                            (y, cat, pda, cc) plus extras
  fe_inventory.csv          end-of-fallow amfe3, gt and gr (mol/m2) in the plough layer (z < 0.2 m) and below, per year,
                            for the 8 controls and the ref 20 t chain (start state as year 0)
  fig5_ref/                 year 1 of the ref control and ref 20 t: porewater/gas/solid profile series (long CSV) and
                            the flx_gas-pch4/pn2o season and fallow flux tables, as read by fig5_dynamics_v22.py
Usage (repository root): python3 paddy/v25/export_v25b.py
"""
import os, sys, glob, json, shutil, csv
import numpy as np

ROOT = os.getcwd()
P = os.path.expanduser('~/fastdata/v25_out/paddy')
OUT = os.path.join(ROOT, 'paddy', 'v25', 'results')
os.makedirs(os.path.join(OUT, 'fig5_ref'), exist_ok=True)
src = open(os.path.join(ROOT, 'paddy', 'ghg_budget.py')).read().split('ctrl = season(args[0])')[0]
src = src.replace('np.loadtxt(f,skiprows=1)', 'np.loadtxt(f,skiprows=1,ndmin=2)')
sys.argv = ['ghg_budget.py']
ns = {}
exec(src, ns)

SITES = ['ref', 'refq1', 'rf189', 'irr061', 'irr043', 'rf184', 'irr092', 'rf151']
CHAINS = []
for s in SITES:
    for d in (['0', '10', '20'] if s in ('ref', 'refq1') else ['0', '20']):
        CHAINS.append(('v25bb', s, d))
for pre in ('v25bbw0', 'v25bbw04'):
    for d in ('0', '10', '20'):
        CHAINS.append((pre, 'ref', d))

def phase(run, days):
    ns['tend'] = days/365.
    return ns['season'](run)

def done(run, tend):
    f = f'{run}/flx/flx_gas-pch4.txt'
    if not os.path.exists(f):
        return False
    lines = [l for l in open(f).read().split('\n')[1:] if l.strip()]
    return bool(lines) and float(lines[-1].split()[0]) >= tend

# 1. per-phase ghg_budget rows
rows, keys = [], None
for pre, s, d in CHAINS:
    for y in range(1, 11):
        for ph, days, tend in (('season', 113., 0.3095), ('fallow', 252., 0.6895)):
            run = f'{P}/flood_{pre}_{s}_{d}_y{y}{ph[0]}'
            if not done(run, tend):
                continue
            o = phase(run, days)
            keys = keys or list(o)
            rows.append([pre, s, d, y, ph] + [o[k] for k in keys])
with open(os.path.join(OUT, 'ghg_phase_rows.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['set', 'site', 'dose_t_ha', 'year', 'phase'] + keys)
    for r in rows:
        w.writerow(r[:5] + [f'{v:.6g}' for v in r[5:]])

# 2. ref timelines (year-round, treatment minus control)
def yr(pre, s, d, y):
    a = {}
    for r in rows:
        if r[0] == pre and r[1] == s and r[2] == d and r[3] == y:
            for k, v in zip(keys, r[5:]):
                a[k] = a.get(k, 0.) + v
    return a
for d in ('10', '20'):
    T = []
    for y in range(1, 11):
        c, t = yr('v25bb', 'ref', '0', y), yr('v25bb', 'ref', d, y)
        if not c or not t:
            continue
        T.append(dict(y=y, cat=t['cation release (t CO2/ha)'],
                      pda=t['potentially durable ALK (t CO2/ha)'] - c['potentially durable ALK (t CO2/ha)'],
                      alk=t['ALK export (t CO2/ha)'] - c['ALK export (t CO2/ha)'],
                      lat=t['lateral ALK (t CO2/ha)'] - c['lateral ALK (t CO2/ha)'],
                      cc=t['calcite (t CO2/ha)'] - c['calcite (t CO2/ha)'],
                      dch4=(t['CH4 (kg/ha)'] - c['CH4 (kg/ha)'])/1e3*27,
                      dn2o=(t['N2O (kg N/ha)'] - c['N2O (kg N/ha)'])*44.01/28.01/1e3*273))
    json.dump(T, open(os.path.join(OUT, f'timeline_ref{d}.json'), 'w'), indent=1)

# 3. Fe inventories, end of each fallow
def sld(f):
    h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
    if len(h) != d.shape[1]:   # restart files: 5-character names run together
        body = open(f).readline().rstrip('\n').split('z', 1)[1].rstrip()
        body = body[:-4] if body.endswith('time') else body
        body = body[1:] if body.startswith(' ') else body
        h = ['z'] + [n for n in (body[i:i + 5].strip() for i in range(0, len(body), 5)) if n]
    return {k: d[:, i] for i, k in enumerate(h) if i < d.shape[1]}
def inv(run):
    rec = sorted(glob.glob(f'{run}/prof/prof_sld-[0-9][0-9][0-9].txt'))
    f = rec[-1] if rec else f'{run}/prof/prof_sld-save.txt'
    if not os.path.exists(f):
        return None
    d = sld(f); z = d['z']; dz = np.gradient(z); pl = z < 0.2
    g = lambda k, m: float(np.sum(d[k][m]*dz[m])) if k in d else 0.
    return [g('amfe3', pl), g('gt', pl), g('gr', pl), g('amfe3', ~pl), g('gt', ~pl), g('gr', ~pl)]
with open(os.path.join(OUT, 'fe_inventory.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['chain', 'year', 'amfe3_plough', 'gt_plough', 'gr_plough', 'amfe3_sub', 'gt_sub', 'gr_sub'])
    for s, d in [(s, '0') for s in SITES] + [('ref', '20')]:
        ch = f'v25bb_{s}_{d}'
        v = inv(f'{P}/flood_{ch}_st')
        if v: w.writerow([ch, 0] + [f'{x:.4f}' for x in v])
        for y in range(1, 11):
            v = inv(f'{P}/flood_{ch}_y{y}f')
            if v: w.writerow([ch, y] + [f'{x:.4f}' for x in v])

# 4. fig 5 inputs: year 1 of ref control and ref 20 t
for d in ('0', '20'):
    for ph in 'sf':
        run = f'{P}/flood_v25bb_ref_{d}_y1{ph}'
        tag = f'ref{d}_y1{ph}'
        for sp in ('pch4', 'pn2o'):
            shutil.copy(f'{run}/flx/flx_gas-{sp}.txt', os.path.join(OUT, 'fig5_ref', f'{tag}_flx_gas-{sp}.txt'))
        with open(os.path.join(OUT, 'fig5_ref', f'{tag}_profiles.csv'), 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['time_yr', 'z_m', 'po2_molL', 'pch4_molL', 'fe2_molL', 'ph', 'amfe3_molm3', 'gt_molm3'])
            G = sorted(glob.glob(f'{run}/prof/prof_gas(aq)-[0-9][0-9][0-9].txt'))
            A = sorted(glob.glob(f'{run}/prof/prof_aq-[0-9][0-9][0-9].txt'))
            S = sorted(glob.glob(f'{run}/prof/prof_sld-[0-9][0-9][0-9].txt'))
            for fg, fa, fs in zip(G, A, S):
                if fg.endswith('-000.txt'):
                    continue
                g, a, sd = sld(fg), sld(fa), sld(fs)
                for i in range(len(g['z'])):
                    w.writerow([f"{g['time'][i]:.6g}", f"{g['z'][i]:.4g}", f"{g['po2'][i]:.4g}", f"{g['pch4'][i]:.4g}",
                                f"{a['fe2'][i]:.4g}", f"{a['ph'][i]:.4g}", f"{sd['amfe3'][i]:.4g}", f"{sd['gt'][i]:.4g}"])
# ferrihydrite and goethite profile after 10 years of the control (fig 5f, 'after 10 more years')
d = sld(sorted(glob.glob(f'{P}/flood_v25bb_ref_0_y10f/prof/prof_sld-[0-9][0-9][0-9].txt'))[-1])
with open(os.path.join(OUT, 'fig5_ref', 'ref0_y10f_end_sld.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['z_m', 'amfe3_molm3', 'gt_molm3'])
    for i in range(len(d['z'])):
        w.writerow([f"{d['z'][i]:.4g}", f"{d['amfe3'][i]:.4g}", f"{d['gt'][i]:.4g}"])
print('wrote', OUT)
