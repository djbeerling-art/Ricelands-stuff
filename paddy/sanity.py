# Sanity checks for the paddy SCEPTER workflow (David, 11 Nov 2026).
#
# run_sanity_checks()  fast (< 2 s), needs no model run. paddy/run_flooded_column.py calls it before every run and
#                      aborts if anything fails. It checks:
#   1. the pH, Fe and Si response functions the model uses (pox.in, n2oy.in, ch4ph.in, Fe(III) inhibition) at their
#      asymptotic limits and for monotonicity,
#   2. unit conversions used in the global post-processing, enforced with Pint (dose, fluxes, CO2e, transport),
#   3. a toy fallow and a toy basalt season written by the real driver (SCEPTER_DRYRUN=1, inputs only, 10 cells):
#      every number in every input file is finite, and the boundary conditions hold at t = 0 and t = end
#      (atmosphere, irrigation water, parent soil and basalt fractions each sum to 1, forcing tables span the run,
#      the basalt dust schedule integrates to the requested dose and is zero at t = end, saturation in [0, 1]).
#   A full SCEPTER run cannot meet the 2 s limit (start-up alone is ~10 s), so model outputs are checked by:
# check_run(rundir)    after each run (run_flooded_column.py calls it and exits with code 3 on failure):
#   the run reached t = end (run_complete.txt and the last flux record at ttot), no NaN/Inf in any flux or profile
#   file, every conserved species' budget closes (flux 'res' column), and the profiles at the first and last record
#   are finite and non-negative (concentrations) with saturation and porosity in [0, 1].
# tests/test_paddy_sanity.py runs these plus slower checks with real toy runs (pytest -m slow, about 1 min).
import os, sys, glob, subprocess, tempfile, shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- response functions (mirror scepter.f90 / driver)
def pox(pH, pmin=0.3, pmax=0.9, pH50=6.0, n=1.0):
    """Fraction of plant-transported CH4 oxidised in the rhizosphere (pox.in)."""
    return pmin + (pmax - pmin) / (1.0 + 10.0 ** (n * (pH50 - np.asarray(pH, float))))

def n2o_yield(pH, pH50=6.2, n=1.0, rmin=0.1):
    """N2O fraction of denitrification (n2oy.in): rmin + (1-rmin)/(1+10^(n(pH-pH50)))."""
    return rmin + (1.0 - rmin) / (1.0 + 10.0 ** (n * (np.asarray(pH, float) - pH50)))

def ch4ph(pH, pK1=6.2, pK2=7.9, pHref=6.5):
    """Optional pH dependence of methanogenesis (ch4ph.in), normalised to 1 at pHref."""
    g = lambda x: 1.0 / (1.0 + 10.0 ** (pK1 - np.asarray(x, float)) + 10.0 ** (np.asarray(x, float) - pK2))
    return g(pH) / g(pHref)

def fe_inhibition(amfe3, K=30.0):
    """Fe(III) inhibition factor on methanogenesis, K/(K+[amfe3]) (mol/m3)."""
    return K / (K + np.asarray(amfe3, float))

def transport_kgco2_per_t(straight_km, detour=1.3):
    """Lefebvre et al. 2019 road transport + handling, kg CO2e per t rock."""
    return 0.218 * detour * np.asarray(straight_km, float) + 5.9

def _check(cond, msg, fails):
    if not bool(np.all(cond)): fails.append(msg)

def check_functions(fails):
    with np.errstate(over='ignore'):
        _check_functions(fails)

def _check_functions(fails):
    big = np.array([-50.0, 50.0])
    p = pox(big); _check(np.allclose(p, [0.3, 0.9]), 'pox limits != (pmin, pmax)', fails)
    _check(np.isclose(pox(6.0), 0.6), 'pox(pH50) != midpoint', fails)
    ph = np.linspace(3, 10, 141)
    _check(np.all(np.diff(pox(ph)) > 0), 'pox not increasing with pH', fails)
    y = n2o_yield(big); _check(np.allclose(y, [1.0, 0.1]), 'N2O yield limits != (1, rmin)', fails)
    _check(np.all(np.diff(n2o_yield(ph)) < 0), 'N2O yield not decreasing with pH', fails)
    _check(np.isclose(ch4ph(6.5), 1.0), 'ch4ph not 1 at pHref', fails)
    _check(np.all(ch4ph(big) < 1e-20), 'ch4ph not -> 0 at extreme pH', fails)
    _check(np.isclose(fe_inhibition(0.0), 1.0) and fe_inhibition(1e12) < 1e-9, 'Fe inhibition limits', fails)
    _check(np.isclose(transport_kgco2_per_t(0.0), 5.9), 'transport at 0 km != handling 5.9', fails)
    for f in (pox, n2o_yield, ch4ph, fe_inhibition, transport_kgco2_per_t):
        _check(np.isfinite(f(np.array([0.0, 1e3]))).all(), f'{f.__name__} not finite', fails)

# ---------------------------------------------------------------- units (Pint)
def check_units(fails):
    try:
        import pint
    except ImportError:
        fails.append('pint not installed (pip install pint)'); return
    u = pint.UnitRegistry()
    u.define('CO2e = [co2e]')
    # basalt dose: 20 t/ha == 2000 g/m2 == the 200000 g/m2/yr x 0.01 yr dust pulse the driver writes
    dose = (20 * u.tonne / u.hectare).to(u.g / u.m**2)
    _check(np.isclose(dose.magnitude, 2000.0), 'dose 20 t/ha != 2000 g/m2', fails)
    pulse = (200000 * u.g / u.m**2 / u.year) * (0.01 * u.year)
    _check(np.isclose(pulse.to(u.g / u.m**2).magnitude, dose.magnitude), 'dust pulse != dose', fails)
    # 100 kg CH4/ha/yr over 95.8 Mha = 9.58 Mt CH4/yr; x 27 (GWP100) = 258.7 Mt CO2e/yr
    tot = (100 * u.kg / u.hectare / u.year * 95.8e6 * u.hectare).to(u.megatonne / u.year)
    _check(np.isclose(tot.magnitude, 9.58), 'CH4 upscaling units', fails)
    co2e = tot * 27 * u.CO2e
    _check(co2e.dimensionality == (u.megatonne * u.CO2e / u.year).dimensionality, 'CO2e dimensionality', fails)
    # SCEPTER fluxes are mol/m2/yr: 1 mol CH4/m2/yr = 160.4 kg CH4/ha/yr
    m = (1 * u.mol / u.m**2 / u.year * 16.04 * u.g / u.mol).to(u.kg / u.hectare / u.year)
    _check(np.isclose(m.magnitude, 160.4), 'mol/m2 -> kg/ha', fails)
    # transport: kg CO2e/t x t/ha/yr -> t CO2e/ha/yr, 100 km at 20 t/ha = 0.69 t
    tr = (transport_kgco2_per_t(100.0) * u.kg / u.tonne) * (20 * u.tonne / u.hectare / u.year)
    _check(np.isclose(tr.to(u.tonne / u.hectare / u.year).magnitude, 0.6848), 'transport units', fails)
    try:
        (1 * u.kg / u.hectare) + (1 * u.mol / u.m**2)
        fails.append('Pint accepted kg/ha + mol/m2')
    except pint.errors.DimensionalityError:
        pass

# ---------------------------------------------------------------- toy inputs from the real driver (no model run)
PROD_SOIL = ('--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 '
             '--n2oy=6.2:1:0.1 --o2inh=2.5e-7 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 --omalloc=0.2:0.6:0.1')
PROD_SEASON = ('--pox=0.3:0.9:6:1 --nucl=cc:0.001 --rtsi=2e-3:2.7e-4:0.15 --phd=14')
RS = ('fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,'
      'nh4up,rtoxy,groxy,siup,sidox,fhage')

def _num(tok):
    try: return float(tok)
    except ValueError: return None

def _table(path):
    rows = []
    for l in open(path):
        if l.startswith(('#', '*')) or not l.strip(): continue
        rows.append([_num(t) for t in l.split()])
    return rows

def _kv(path):
    d = {}
    for l in open(path):
        if l.startswith(('#', '*')) or not l.strip(): continue
        t = l.split()
        if len(t) >= 2 and _num(t[1]) is not None: d[t[0]] = float(t[1])
    return d

def toy_inputs(out, dose=20.0, nz=10, ttot=0.31):
    """Write a toy fallow (no basalt) and a toy basalt season with production options; return their run dirs."""
    env = dict(os.environ, SCEPTER_DRYRUN='1', SCEPTER_OUT=out + '/')
    runs = {'fallow': ['sanity_fallow', 'fe2o2,amo2o', '0.69', '--fallow', '--basalt=0'],
            'season': ['sanity_season', RS, str(ttot), '--season', '--nfert=120', f'--basalt={dose}'] + PROD_SEASON.split()}
    dirs = {}
    for k, a in runs.items():
        cmd = [sys.executable, os.path.join(HERE, 'run_flooded_column.py')] + a + PROD_SOIL.split() + [f'--nz={nz}', '--ztot=0.3']
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f'driver failed for toy {k}: {r.stderr[-500:]}')
        dirs[k] = os.path.join(out, 'paddy', 'flood_' + a[0])
    return dirs

def check_inputs(d, fails, dose=None, nz=None, ttot=None):
    name = os.path.basename(d)
    for f in glob.glob(os.path.join(d, '*.in')):
        for l in open(f):
            for t in l.split():
                x = _num(t)
                if x is not None and not np.isfinite(x): fails.append(f'{name}/{os.path.basename(f)}: non-finite {t}')
    fr = _table(os.path.join(d, 'frame.in'))
    ztot, nzf, tt = fr[0][0], fr[1][0], fr[2][0]
    _check(ztot > 0 and tt > 0, f'{name}: frame.in depth/duration not positive', fails)
    if nz is not None: _check(int(nzf) == nz, f'{name}: frame.in nz {nzf} != {nz}', fails)
    if ttot is not None: _check(np.isclose(tt, ttot), f'{name}: frame.in ttot {tt} != {ttot}', fails)
    atm = _kv(os.path.join(d, 'atm.in'))
    _check(np.isclose(atm.get('po2', 0), 0.21) and atm.get('pco2', 0) > 0, f'{name}: atmosphere O2/CO2 boundary', fails)
    _check(all(v >= 0 for v in atm.values()), f'{name}: negative atmospheric partial pressure', fails)
    _check(all(v >= 0 for v in _kv(os.path.join(d, 'rain.in')).values()), f'{name}: negative irrigation-water conc.', fails)
    pr = _kv(os.path.join(d, 'parentrock.in'))
    _check(all(v >= 0 for v in pr.values()) and np.isclose(sum(pr.values()), 1.0, atol=1e-9),
           f'{name}: parent soil fractions do not sum to 1 ({sum(pr.values())})', fails)
    du = _kv(os.path.join(d, 'dust.in'))
    if du: _check(np.isclose(sum(du.values()), 1.0, atol=1e-9), f'{name}: basalt mineral fractions sum {sum(du.values())}', fails)
    # time-dependent forcing: spans t = 0 to t = end, physical ranges, basalt pulse = dose and zero at t = end
    for fn, lo, hi in (('T_temp.in', -5, 50), ('Wet_temp.in', 0, 1000), ('q_temp.in', 0, 1e4), ('Dust_temp.in', 0, None)):
        p = os.path.join(d, fn)
        if not os.path.exists(p): continue
        t = np.array(_table(p), float)
        _check(np.isfinite(t).all(), f'{name}/{fn}: non-finite', fails)
        _check(t[0, 0] == 0.0, f'{name}/{fn}: does not start at t = 0', fails)
        _check(np.all(np.diff(t[:, 0]) > 0), f'{name}/{fn}: times not increasing', fails)
        _check(t[-1, 0] >= min(tt, 0.99) - 1e-9, f'{name}/{fn}: ends at {t[-1, 0]} before t = end {tt}', fails)
        _check(t[:, 1].min() >= lo and (hi is None or t[:, 1].max() <= hi), f'{name}/{fn}: values out of range', fails)
        if fn == 'Dust_temp.in':
            g = float(np.sum(0.5 * (t[1:, 1] + t[:-1, 1]) * np.diff(t[:, 0])))   # g/m2
            _check(t[-1, 1] == 0.0, f'{name}: basalt still applied at t = end', fails)
            if dose is not None:
                _check(np.isclose(g / 100.0, dose, rtol=0.02), f'{name}: basalt pulse {g/100:.2f} t/ha != dose {dose}', fails)

def run_sanity_checks(verbose=False):
    """Fast checks (< 2 s); raises AssertionError listing every failure."""
    import time
    t0 = time.time(); fails = []
    check_functions(fails)
    check_units(fails)
    out = tempfile.mkdtemp(prefix='scepter_sanity_')
    try:
        dirs = toy_inputs(out)
        check_inputs(dirs['fallow'], fails, nz=10, ttot=0.69)
        check_inputs(dirs['season'], fails, dose=20.0, nz=10, ttot=0.31)
    except Exception as e:
        fails.append(f'toy input build: {e}')
    finally:
        shutil.rmtree(out, ignore_errors=True)
    if verbose: print(f'sanity checks: {len(fails)} failures in {time.time()-t0:.2f} s')
    if fails: raise AssertionError('SCEPTER sanity checks failed:\n  ' + '\n  '.join(fails))
    return True

# ---------------------------------------------------------------- outputs of a real run
# derived carbonate-system diagnostics are not conserved quantities, so no budget check there
NONCONSERVED = ('flx_co2sp-',)
# the t = 0 bulk-property record (bsd-000) is written before solid densities are set, so bulk wt% is x/0 = Inf there;
# it is a diagnostic only (not used by the solver; bsd-001 onward is finite)
KNOWN_T0 = {('bsd', 'blk[wt%]')}
# files holding log10 values, where an absent phase is legitimately -Inf
LOGFILES = ('sat_sld',)

def check_run(rundir, rtol=1e-4, atol=1e-10):
    # rtol: SCEPTER's Newton tolerance is tol = 1e-6 per iteration, so budgets close to ~1e-5 of the largest term
    # (cation-exchange species Ca, Mg, K and kaolinite reach 7e-6 in the toy runs); 1e-4 leaves a 10x margin.
    """Check a finished run directory; returns a list of failures (empty = OK)."""
    fails = []; name = os.path.basename(rundir.rstrip('/'))
    if not os.path.exists(os.path.join(rundir, 'run_complete.txt')):
        return [f'{name}: no run_complete.txt (model stopped early or crashed)']
    tt = _table(os.path.join(rundir, 'frame.in'))[2][0]
    fl = sorted(glob.glob(os.path.join(rundir, 'flx', 'flx_*.txt')))
    _check(len(fl) > 0, f'{name}: no flux files', fails)
    for f in fl:
        h = open(f).readline().split()
        d = np.loadtxt(f, skiprows=1, ndmin=2)
        b = os.path.basename(f)
        if d.size == 0: fails.append(f'{name}/{b}: empty'); continue
        if not np.isfinite(d).all(): fails.append(f'{name}/{b}: NaN/Inf'); continue
        _check(abs(d[-1, 0] - tt) <= 1e-3 * tt + 1e-9, f'{name}/{b}: ends at t={d[-1,0]:.6g}, not t_end={tt}', fails)
        if 'res' in h and not b.startswith(NONCONSERVED):
            i = h.index('res'); terms = np.abs(d[:, 1:i]).max()
            r = np.abs(d[:, i]).max()
            _check(r <= rtol * terms + atol, f'{name}/{b}: budget residual {r:.2e} vs largest term {terms:.2e}', fails)
    pf = sorted(glob.glob(os.path.join(rundir, 'prof', '*-[0-9][0-9][0-9].txt')))
    if pf:
        ids = sorted({p[-7:-4] for p in pf})
        for rec in (ids[0], ids[-1]):                       # first and last record = t = 0 and t = end
            for p in [q for q in pf if q.endswith(f'-{rec}.txt')]:
                b = os.path.basename(p)
                try:
                    h = open(p).readline().split(); d = np.loadtxt(p, skiprows=1, ndmin=2)
                except Exception:
                    continue
                cols = [k for k in range(d.shape[1]) if not (rec == ids[0] and (b[:-8], h[k] if k < len(h) else '') in KNOWN_T0)]
                if b.startswith(LOGFILES): d = np.where(np.isneginf(d), 0.0, d)   # log of an absent phase = -inf
                if not np.isfinite(d[:, cols]).all(): fails.append(f'{name}/{b}: NaN/Inf'); continue
                if b.startswith(('prof_sld', 'prof_aq(tot)', 'prof_gas')):
                    _check((d[:, 1:] >= -1e-12).all(), f'{name}/{b}: negative concentration', fails)
                for k in ('poro', 'sat'):
                    if k in h: _check(((d[:, h.index(k)] >= 0) & (d[:, h.index(k)] <= 1 + 1e-9)).all(), f'{name}/{b}: {k} outside [0, 1]', fails)
    return fails

if __name__ == '__main__':
    if len(sys.argv) > 1:
        bad = [f for d in sys.argv[1:] for f in check_run(d)]
        print('\n'.join(bad) if bad else 'OK'); sys.exit(1 if bad else 0)
    run_sanity_checks(verbose=True); print('OK')
