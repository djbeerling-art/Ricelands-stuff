"""Summarise the arsenic sweep (paddy/arsenic/run_as_sweep.sh) into the basalt response map.

For every soil and chain year it compares basalt (d<dose>) with control (d0) season runs and reports, separately:
  - porewater: season-mean As(III), Si and pH over the root zone (0-ZROOT m), and R_As = As(III) basalt / control
  - Si-inhibition threshold T = (1 + Si_basalt/Ki) / (1 + Si_control/Ki), Ki = 300 uM (siup half-saturation)
  - competitive uptake ratio R_As/T, and the simulated As(III) uptake ratio from the as3up flux (int_flx_aq-as3)
  - grain iAs: not modelled yet (translocation, OsABCC1, Si down-regulation of Lsi1/Lsi2) -> column left empty
Class: 'suppress' if uptake ratio < 1/(1+BAND), 'mobilise' if > 1+BAND, else 'uncertain' (BAND default 0.15).
Usage: python3 paddy/arsenic/as_sweep_summary.py <SCEPTER_OUT>/paddy [dose] > as_sweep_summary.csv
"""
import sys, os, glob, re, csv
import numpy as np

root = sys.argv[1]; dose = sys.argv[2] if len(sys.argv) > 2 else '20'
ZROOT, KI, BAND = 0.2, 300.0, 0.15

def season_means(run):
    fs = sorted(glob.glob(os.path.join(run, 'prof', 'prof_aq-[0-9]*.txt')))
    if not fs: return None
    acc = {'as3': [], 'si': [], 'ph': []}
    for f in fs:
        h = open(f).readline().split(); a = np.atleast_2d(np.loadtxt(f, skiprows=1))
        m = a[:, 0] <= ZROOT
        for k in acc:
            if k in h: acc[k].append(a[m, h.index(k)].mean())
    return {k: (float(np.mean(v)) if v else np.nan) for k, v in acc.items()}

def uptake(run):
    f = os.path.join(run, 'flx', 'int_flx_aq-as3.txt')
    if not os.path.exists(f): return np.nan
    h = open(f).readline().split(); a = np.atleast_2d(np.loadtxt(f, skiprows=1))
    return float(abs(a[-1, h.index('as3up')])) if 'as3up' in h else np.nan

w = csv.writer(sys.stdout)
w.writerow(['soil', 'fe3_wt', 'gt_wt', 'irralk', 'year', 'pH_ctrl', 'pH_bas', 'Si_ctrl_uM', 'Si_bas_uM',
            'As3_ctrl_uM', 'As3_bas_uM', 'R_As', 'T_Si', 'uptake_ratio_competitive', 'uptake_ratio_simulated',
            'grain_iAs_ratio', 'class'])
for d0 in sorted(glob.glob(os.path.join(root, 'flood_as_f*_d0_y*s'))):
    m = re.search(r'flood_(as_f([\d.]+)_g([\d.]+)_a([\d.]+))_d0_y(\d+)s$', d0)
    if not m: continue
    tag, f, g, a, y = m.groups()
    db = os.path.join(root, f'flood_{tag}_d{dose}_y{y}s')
    c, b = season_means(d0), season_means(db) if os.path.isdir(db) else None
    if c is None or b is None: continue
    ra = b['as3'] / c['as3']; T = (1 + b['si']*1e6/KI) / (1 + c['si']*1e6/KI)
    uc = ra / T; uc_ctrl, ub = uptake(d0), uptake(db); us = ub / uc_ctrl if uc_ctrl else np.nan
    u = us if np.isfinite(us) else uc
    cls = 'suppress' if u < 1/(1+BAND) else ('mobilise' if u > 1+BAND else 'uncertain')
    w.writerow([tag, f, g, a, y, round(c['ph'], 2), round(b['ph'], 2), round(c['si']*1e6), round(b['si']*1e6),
                '%.4g' % (c['as3']*1e6), '%.4g' % (b['as3']*1e6), round(ra, 2), round(T, 2), round(uc, 2),
                round(us, 2) if np.isfinite(us) else '', '', cls])
