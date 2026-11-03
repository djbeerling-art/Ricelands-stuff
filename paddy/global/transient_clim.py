# Transient (year-by-year) monthly climate for the future cases (David, 2 Nov 2026: "go out to 2050"): each archetype's
# climate steps linearly from the present-day baseline (ERA5-Land 1995-2014, centred on TBASE = 2005) towards the
# case's 2041-2060 climatology (baseline + CMIP6 deltas, centred on TFUT = 2050), one file per model year.
#   value(year) = base + (fut - base) * (year - TBASE) / (TFUT - TBASE)   (all columns: tsoil_C, wsat, p_mm, et_mm)
# Model year N (1..NY) is calendar year Y0 + N - 1. Files: <archdir>/clim/<case>_tr/<arch>_y<N>.csv, plus <arch>.csv =
# year 1 (for anything that reads --clim directly). run_chain.sh picks <stem>_y<N>.csv for chain year N (+CLIM_YOFF,
# clamped to 1..NY) whenever such files exist next to the --clim file, so the dose chains follow the trajectory and the
# re-settle (CLIM_YOFF=-RESETTLE in run_arch_v22.sh) runs under the first year's climate.
# Usage: python3 transient_clim.py <archdir> <case e.g. GFDL-ESM4_ssp245_2041-2060> [--y0=2026] [--ny=25] [--tbase=2005] [--tfut=2050]
#   -> <archdir>/clim/<case>_tr/*.csv and <archdir>/archetypes_<case>_tr.csv (args with --clim pointing at <arch>.csv)
import sys, os, re
import pandas as pd

def opt(k, d):
    for a in sys.argv[1:]:
        if a.startswith(f'--{k}='): return a.split('=', 1)[1]
    return d

def main(archdir, case):
    y0, ny = int(opt('y0', 2026)), int(opt('ny', 25))
    tb, tf = float(opt('tbase', 2005)), float(opt('tfut', 2050))
    bdir, fdir = os.path.join(archdir, 'clim', 'baseline'), os.path.join(archdir, 'clim', case)
    odir = os.path.join(archdir, 'clim', case + '_tr'); os.makedirs(odir, exist_ok=True)
    a = pd.read_csv(os.path.join(archdir, f'archetypes_{case}.csv'))
    for arch in a.arch:
        b = pd.read_csv(os.path.join(bdir, f'{arch}.csv')).set_index('month')
        f = pd.read_csv(os.path.join(fdir, f'{arch}.csv')).set_index('month')
        for n in range(1, ny + 1):
            w = (y0 + n - 1 - tb)/(tf - tb)
            c = (b + (f - b)*w).round(4)
            c.to_csv(os.path.join(odir, f'{arch}_y{n}.csv'))
            if n == 1: c.to_csv(os.path.join(odir, f'{arch}.csv'))
    a['args'] = [re.sub(r'--clim=\S+', f'--clim={odir}/{r.arch}.csv', r.args) for r in a.itertuples()]
    out = os.path.join(archdir, f'archetypes_{case}_tr.csv'); a.to_csv(out, index=False)
    w1, wn = (y0 - tb)/(tf - tb), (y0 + ny - 1 - tb)/(tf - tb)
    print(f'{case}: {len(a)} archetypes x {ny} yr ({y0}-{y0+ny-1}; {w1:.2f}-{wn:.2f} of the way to {case}) -> {out}')

if __name__ == '__main__':
    main(*[x for x in sys.argv[1:] if not x.startswith('--')])
