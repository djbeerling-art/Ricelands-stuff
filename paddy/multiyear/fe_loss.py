#!/usr/bin/env python3
# Net Fe transported out of the plough layer over one or more runs (dynamic Fe return, run_chain.sh FERET=1).
# From the per-cell time-integrated flux terms flx/zint_aq-fe2.txt and zint_aq-fe3.txt (mol m-2 over each run): the
# transport terms (adv + dif) of the cells above the plane sum to (flux out through the plane, i.e. across the pan,
# plus floodwater discharge at the surface) minus inflow with irrigation water, as in paddy/plane_flux.py.
# Usage: fe_loss.py <run dir> [<run dir> ...] [--z=0.2]  -> prints the total (mol Fe m-2)
import sys, os
import pandas as pd
opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
zp = float(opt.get('z', 0.2))
tot = 0.
for r in [a for a in sys.argv[1:] if not a.startswith('--')]:
    for sp in ('fe2', 'fe3'):
        f = os.path.join(r, 'flx', f'zint_aq-{sp}.txt')
        if not os.path.exists(f):
            if sp == 'fe2': sys.exit(f'fe_loss.py: missing {f}')
            continue
        d = pd.read_csv(f, sep=r'\s+')
        m = d['z'] <= zp + 1e-6
        tot += float(sum(d[c][m].sum() for c in ('adv', 'dif') if c in d))
print(f'{tot:.5f}')
