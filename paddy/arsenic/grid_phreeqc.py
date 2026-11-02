"""Generate a PHREEQC (Dzombak & Morel DLM) grid of As(III), As(V) and Si sorption on ferrihydrite
for fitting SCEPTER's non-electrostatic competitive scheme. P held low (0.01 mM; SCEPTER carries no P)."""
import sys, csv, itertools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hfo_as_si import run
rows = []
for pH, si, asm, fe, f5 in itertools.product(
        (5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0),
        (0.02, 0.1, 0.3, 0.6, 1.0, 1.5, 2.0),
        (0.002, 0.02, 0.2),
        (0.233, 0.07, 0.023),
        (0.05, 0.5)):
    r = run(pH=pH, si_mM=si, p_mM=0.01, as_mM=asm, fe_mol=fe, as5_frac=f5)
    if r is None: continue
    rows.append(dict(pH=pH, si_mM=si, as_mM=asm, fe_mol=fe, as5_frac=f5,
                     as3_uM=r['As3_uM'], as5_uM=r['As5_uM'], si_uM=r['Si_uM']))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grid_phreeqc.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows))
