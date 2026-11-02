"""Summarise the arsenic sweep (paddy/arsenic/run_as_sweep.sh): one row per soil and treatment year.

Diagnostics (basalt B vs control C, root zone 0-ZROOT m, root-density weighted exp(-z/0.1) as ch4pl/siup):
  R_As      season-mean porewater As(III) B/C                         (geochemical mobilisation)
  R_Si, dpH season-mean Si B/C and pH B-C                             (dissolved Si response, alkalinisation)
  T         (1 + Si_B/Ki)/(1 + Si_C/Ki) from season means, Ki = 300 uM (maximum mobilisation compatible with suppression)
  R_up_Ki*  competitive uptake ratio from TIME-RESOLVED values: integral over time and roots of As3/(1 + Si/Ki), B/C,
            for Ki = 150, 300, 600 uM (linear in As(III): Km_As >> porewater As(III))
  log10 decomposition: log R_up(Ki 300) = log R_As,eff - log T_eff, where R_As,eff = time-integrated As(III) B/C and
            T_eff = R_As,eff / R_up (the Si-inhibition term from the time-resolved series)
  R_up_sim  As(III) uptake from the model's as3up flux, B/C (int_flx_aq-as3: time-averaged rate x time)
  budget    per run (mol As m-2, As(III)+As(V)): percolating irrigation input (rain.in concs x q x t), net transport
            gain (-(adv+dif) x t: percolation input + floodwater exchange (irrigation-renewed floodwater, lateral
            discharge) - drainage at the base), plant uptake, change in sorbed and dissolved inventory, closure residual
  class     'suppress' / 'mobilise' if every uptake estimate (Ki 150/300/600 and simulated) is below / above 1;
            'uncertain (uptake parameters)' if they disagree: uptake-parameter uncertainty only, not Fe sorption,
            As(V) reduction or grain partitioning
  grain iAs not modelled yet (translocation, Lsi1/Lsi2 regulation, node sequestration) -> empty
Usage: python3 paddy/arsenic/as_sweep_summary.py <SCEPTER_OUT>/paddy [dose] > as_sweep_summary.csv
"""
import sys, os, glob, re, csv
import numpy as np
_trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")

root = sys.argv[1]; dose = sys.argv[2] if len(sys.argv) > 2 else '20'
ZROOT, ZR = 0.2, 0.1
KIS = (150.0, 300.0, 600.0)

def series(run):
    """time-resolved root-weighted As(III), Si (M) and pH over the root zone"""
    fs = sorted(glob.glob(os.path.join(run, 'prof', 'prof_aq-[0-9]*.txt')))
    t, a3, si, ph, z, w = [], [], [], [], None, None
    for f in fs:
        h = open(f).readline().split(); a = np.atleast_2d(np.loadtxt(f, skiprows=1))
        if z is None:
            z = a[:, 0]; w = np.exp(-z/ZR)*(z <= ZROOT); w = w/w.sum()
        t.append(a[0, h.index('time')]); a3.append(a[:, h.index('as3')]); si.append(a[:, h.index('si')]); ph.append(a[:, h.index('ph')])
    if not t: return None
    return dict(t=np.array(t), as3=np.array(a3), si=np.array(si), ph=np.array(ph), w=w)

def tint(s, x):
    """time integral (trapezoid) of a root-weighted profile quantity x[t, z]"""
    v = (x*s['w']).sum(axis=1)
    return _trap(v, s["t"]) if len(v) > 1 else v[0]

def mean(s, x): return tint(s, x)/(s['t'][-1] - s['t'][0]) if len(s['t']) > 1 else (x*s['w']).sum()

def intflx(run, name):
    f = os.path.join(run, 'flx', f'int_flx_{name}.txt')
    if not os.path.exists(f): return None
    h = open(f).readline().split(); a = np.atleast_2d(np.loadtxt(f, skiprows=1))
    return {k: a[-1, i]*a[-1, 0] for i, k in enumerate(h) if k != 'time'}   # time-averaged rate x time = total

def budget(run):
    a3, a5, s3, s5 = (intflx(run, n) for n in ('aq-as3', 'aq-as5', 'sld-as3ad', 'sld-as5ad'))
    if a3 is None or a5 is None: return {}
    conc = {l.split()[0]: float(l.split()[1]) for l in open(os.path.join(run, 'rain.in')).readlines()[1:] if len(l.split()) > 1}
    fr = open(os.path.join(run, 'frame.in')).readlines()
    ttot, q = float(fr[3].split()[0]), float(fr[15].split()[0])
    inp = (conc.get('as3', 0) + conc.get('as5', 0))*1e3*q*ttot
    gain = -(a3.get('adv', 0) + a3.get('dif', 0) + a5.get('adv', 0) + a5.get('dif', 0))
    upt = a3.get('as3up', 0)
    dsorb = (s3['tflx'] + s5['tflx']) if s3 and s5 else np.nan
    ddis = a3['tflx'] + a5['tflx']
    return dict(input_perc=inp, net_transport_gain=gain, uptake=upt, d_sorbed=dsorb, d_dissolved=ddis,
                residual=gain - upt - dsorb - ddis)

w = csv.writer(sys.stdout)
cols = ['soil', 'fe3_wt', 'gt_wt', 'irralk', 'year', 'pH_C', 'dpH', 'Si_C_uM', 'R_Si', 'As3_C_uM', 'R_As', 'T',
        'R_up_Ki150', 'R_up_Ki300', 'R_up_Ki600', 'R_up_sim', 'log10R_As_eff', 'log10T_eff', 'log10R_up', 'class',
        'grain_iAs_ratio']
for tr in ('C', 'B'):
    cols += [f'{tr}_{k}_molm2' for k in ('input_perc', 'net_transport_gain', 'uptake', 'd_sorbed', 'd_dissolved', 'residual')]
w.writerow(cols)
for d0 in sorted(glob.glob(os.path.join(root, 'flood_as_f*_d0_y*s'))):
    m = re.search(r'flood_(as_f([\d.]+)_g([\d.]+)_a([\d.]+))_d0_y(\d+)s$', d0)
    if not m: continue
    tag, f, g, a, y = m.groups()
    db = os.path.join(root, f'flood_{tag}_d{dose}_y{y}s')
    if not os.path.isdir(db): continue
    c, b = series(d0), series(db)
    if c is None or b is None: continue
    sc, sb = mean(c, c['si']), mean(b, b['si'])
    ra = mean(b, b['as3'])/mean(c, c['as3']); T = (1 + sb*1e6/300)/(1 + sc*1e6/300)
    rup = {ki: tint(b, b['as3']/(1 + b['si']*1e6/ki))/tint(c, c['as3']/(1 + c['si']*1e6/ki)) for ki in KIS}
    ra_eff = tint(b, b['as3'])/tint(c, c['as3']); t_eff = ra_eff/rup[300.0]
    bc, bb = budget(d0), budget(db)
    us = bb.get('uptake', np.nan)/bc['uptake'] if bc.get('uptake') else np.nan
    est = list(rup.values()) + ([us] if np.isfinite(us) else [])
    cls = 'suppress' if max(est) < 1 else ('mobilise' if min(est) > 1 else 'uncertain (uptake parameters)')
    row = [tag, f, g, a, y, round(mean(c, c['ph']), 2), round(mean(b, b['ph']) - mean(c, c['ph']), 2), round(sc*1e6),
           round(sb/sc, 2), '%.4g' % (mean(c, c['as3'])*1e6), round(ra, 3), round(T, 3),
           *[round(rup[k], 3) for k in KIS], round(us, 3) if np.isfinite(us) else '',
           round(np.log10(ra_eff), 3), round(np.log10(t_eff), 3), round(np.log10(rup[300.0]), 3), cls, '']
    for bd in (bc, bb):
        row += ['%.4g' % bd.get(k, np.nan) for k in ('input_perc', 'net_transport_gain', 'uptake', 'd_sorbed', 'd_dissolved', 'residual')]
    w.writerow(row)
