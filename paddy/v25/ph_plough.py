#!/usr/bin/env python3
"""Plough-layer (0-0.20 m) porewater pH per profile record for the v25b reference 10-yr season runs.
Mean of cell pH weighted by cell thickness over z < 0.2 m. Writes paddy/v25/results/ph_plough_ref.csv
(chain, dose, year, rec, time_yr, ph_0_20) and the 30-row summary ph_plough_ref_summary.csv: pH at the last record
before the pre-harvest drain (end of flooding, t <= (113-14)/365 yr; same sampling time every year) and the flooded-period
mean. Usage (repository root): python3 paddy/v25/ph_plough.py [out dir]"""
import os, sys, glob, csv
import numpy as np
P = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/fastdata/v25_out/paddy')
OUT = os.path.join(os.getcwd(), 'paddy', 'v25', 'results', 'ph_plough_ref.csv')
rows = []
for d in ('0', '10', '20'):
    for y in range(1, 11):
        run = f'{P}/flood_v25bb_ref_{d}_y{y}s'
        for f in sorted(glob.glob(f'{run}/prof/prof_aq-[0-9][0-9][0-9].txt')):
            h = open(f).readline().split(); a = np.loadtxt(f, skiprows=1, ndmin=2)
            c = {k: a[:, i] for i, k in enumerate(h)}
            z = c['z']; dz = np.gradient(z); m = z < 0.2
            rows.append([f'v25bb_ref_{d}', d, y, os.path.basename(f)[8:11], f"{c['time'][0]:.5f}",
                         f"{np.sum(c['ph'][m]*dz[m])/np.sum(dz[m]):.4f}"])
with open(OUT, 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['chain', 'dose_t_ha', 'year', 'rec', 'time_yr', 'ph_0_20']); w.writerows(rows)
SUM = OUT.replace('.csv', '_summary.csv'); tflood = (113. - 14.)/365.
with open(SUM, 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['dose_t_ha', 'year', 'time_end_flood_yr', 'ph_end_flood_0_20', 'ph_mean_flooded_0_20'])
    for d in ('0', '10', '20'):
        for y in range(1, 11):
            R = [r for r in rows if r[1] == d and r[2] == y and 0 < float(r[4]) <= tflood + 1e-6]
            if R:
                w.writerow([d, y, R[-1][4], R[-1][5], f"{np.mean([float(r[5]) for r in R]):.4f}"])
print('wrote', OUT, len(rows), 'rows;', SUM)
print(open(SUM).read())
