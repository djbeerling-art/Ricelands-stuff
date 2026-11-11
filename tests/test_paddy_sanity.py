# Tests for the paddy SCEPTER workflow (David, 11 Nov 2026). Run from the repository root:
#   pytest -q tests/test_paddy_sanity.py              fast tests only (a few seconds)
#   pytest -q -m slow tests/test_paddy_sanity.py      real toy model runs (about 1-2 min; builds scepter_paddy_fast if missing)
# Covers: conservation (every flux budget closes), asymptotic limits (response functions; basalt dose -> 0 equals
# the control), dimensional consistency (Pint), and edge-case grids (tiny columns, short runs) for NaN/Inf.
import os, sys, shutil, subprocess, time
import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'paddy'))
import sanity  # noqa: E402

EXE = 'scepter_paddy_fast'

# ------------------------------------------------------------------ fast tests
def test_run_sanity_checks_fast():
    t0 = time.time()
    assert sanity.run_sanity_checks()
    assert time.time() - t0 < 2.0, 'run_sanity_checks must take < 2 s'

@pytest.mark.parametrize('f,lo,hi', [
    (sanity.pox, 0.3, 0.9),            # pH -> -inf: pmin; pH -> +inf: pmax
    (sanity.n2o_yield, 1.0, 0.1),      # acid: all denitrified N as N2O; alkaline: rmin
])
def test_ph_function_limits(f, lo, hi):
    with np.errstate(over='ignore'):
        assert np.isclose(f(-100.0), lo) and np.isclose(f(100.0), hi)

def test_ch4ph_normalised_and_bounded():
    with np.errstate(over='ignore'):
        assert np.isclose(sanity.ch4ph(6.5), 1.0)
        assert sanity.ch4ph(-100.0) < 1e-50 and sanity.ch4ph(100.0) < 1e-50

def test_fe_inhibition_limits():
    assert sanity.fe_inhibition(0.0) == 1.0
    assert np.isclose(sanity.fe_inhibition(30.0), 0.5)          # half-saturation at K
    assert sanity.fe_inhibition(1e15) < 1e-12

def test_units():
    pytest.importorskip('pint')
    fails = []; sanity.check_units(fails)
    assert not fails, fails

def test_units_reject_mismatch():
    pint = pytest.importorskip('pint')
    u = pint.UnitRegistry()
    with pytest.raises(pint.errors.DimensionalityError):
        (1 * u.kg / u.hectare / u.year).to(u.mol / u.m**2 / u.year)

@pytest.fixture(scope='module')
def toy_dirs(tmp_path_factory):
    out = str(tmp_path_factory.mktemp('toyin'))
    return sanity.toy_inputs(out)

def test_toy_inputs_pass(toy_dirs):
    fails = []
    sanity.check_inputs(toy_dirs['season'], fails, dose=20.0, nz=10, ttot=0.31)
    sanity.check_inputs(toy_dirs['fallow'], fails, nz=10, ttot=0.69)
    assert not fails, fails

def test_inputs_catch_nan_and_bad_boundaries(toy_dirs, tmp_path):
    d = str(tmp_path / 'bad'); shutil.copytree(toy_dirs['season'], d)
    with open(os.path.join(d, 'parentrock.in'), 'a') as f: f.write('cc\tnan\n')
    with open(os.path.join(d, 'atm.in')) as f: s = f.read()
    with open(os.path.join(d, 'atm.in'), 'w') as f: f.write(s.replace('po2\t0.21', 'po2\t0.5'))
    fails = []; sanity.check_inputs(d, fails, dose=10.0)
    txt = '\n'.join(fails)
    assert 'non-finite' in txt and 'atmosphere' in txt and 'dose' in txt

def test_check_run_catches_nan_and_unclosed_budget(tmp_path):
    d = tmp_path / 'flood_fake'; (d / 'flx').mkdir(parents=True)
    (d / 'run_complete.txt').write_text('done\n')
    (d / 'frame.in').write_text('** x\n0.3\tdepth\n10\tnz\n0.1\tttot\n')
    (d / 'flx' / 'flx_gas-pch4.txt').write_text('time tflx dif res\n0.05 1.0 -1.0 0.0\n0.1 nan -1.0 0.0\n')
    (d / 'flx' / 'flx_gas-po2.txt').write_text('time tflx dif res\n0.05 1.0 -1.0 0.0\n0.1 1.0 -1.0 0.5\n')
    fails = sanity.check_run(str(d))
    assert any('NaN' in f for f in fails) and any('residual' in f for f in fails)

def test_check_run_catches_early_stop(tmp_path):
    d = tmp_path / 'flood_crashed'; d.mkdir()
    assert any('run_complete' in f for f in sanity.check_run(str(d)))

# ------------------------------------------------------------------ slow tests: real toy runs
SOIL = sanity.PROD_SOIL.split()
SEASON = ['--k=paddy/krxn_calibrated_v25b.in'] + sanity.PROD_SEASON.split()

def _run(out, args, timeout=600):
    env = dict(os.environ, SCEPTER_OUT=out + '/', SCEPTER_SANITY='0')
    r = subprocess.run([sys.executable, 'paddy/run_flooded_column.py'] + args + [f'--exe={EXE}'],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
    return r, os.path.join(out, 'paddy', 'flood_' + args[0])

@pytest.fixture(scope='module')
def model(tmp_path_factory):
    if not shutil.which('gfortran'): pytest.skip('gfortran not available')
    if not os.path.exists(os.path.join(ROOT, EXE)):
        subprocess.run(['make', '-s', '--file=makefile_paddy_fast'], cwd=ROOT, check=True, capture_output=True)
    out = str(tmp_path_factory.mktemp('toyrun'))
    r, spin = _run(out, ['tspin', 'fe2o2,amo2o', '0.05', '--fallow', '--basalt=0'] + SOIL + ['--nz=10'])
    assert os.path.exists(os.path.join(spin, 'run_complete.txt')), r.stderr[-500:]
    runs = {}
    for tag, dose in (('t0', '0'), ('t1e6', '1e-6'), ('t20', '20')):
        r, d = _run(out, [tag, sanity.RS, '0.02', '--season', '--nfert=120', '--rstrt=tspin', f'--basalt={dose}']
                    + SOIL + SEASON + ['--nz=10'])
        runs[tag] = d
    return out, spin, runs

def _emis(d):
    f = os.path.join(d, 'flx', 'flx_gas-pch4.txt')
    h = open(f).readline().split(); a = np.loadtxt(f, skiprows=1, ndmin=2)
    dt = np.diff(np.concatenate([[0.0], a[:, 0]]))
    return sum(float((a[:, h.index(k)] * dt).sum()) for k in ('dif', 'ch4eb', 'ch4pl') if k in h)

@pytest.mark.slow
def test_spinup_output_clean(model):
    assert sanity.check_run(model[1]) == []

@pytest.mark.slow
@pytest.mark.parametrize('tag', ['t0', 't1e6', 't20'])
def test_season_conservation_and_finite(model, tag):
    # every conserved species' budget closes to 1e-4 of its largest term (solver tolerance 1e-6 per iteration); no NaN/Inf; t_end reached
    assert sanity.check_run(model[2][tag]) == []

@pytest.mark.slow
def test_dose_to_zero_limit(model):
    # asymptotic limit: a vanishing basalt dose must reproduce the control
    e0, e1 = _emis(model[2]['t0']), _emis(model[2]['t1e6'])
    assert np.isclose(e0, e1, rtol=1e-4, atol=1e-12), (e0, e1)

@pytest.mark.slow
def test_basalt_does_not_raise_ch4_production(model):
    def prod(d):
        f = os.path.join(d, 'flx', 'flx_gas-pch4.txt'); h = open(f).readline().split()
        a = np.loadtxt(f, skiprows=1, ndmin=2); dt = np.diff(np.concatenate([[0.0], a[:, 0]]))
        return float((a[:, h.index('g2ch4')] * dt).sum())
    # budget sign convention: sources are negative, so compare magnitudes
    assert abs(prod(model[2]['t20'])) <= abs(prod(model[2]['t0'])) * (1 + 1e-6)

@pytest.mark.slow
@pytest.mark.parametrize('nz', [3, 5, 8])
@pytest.mark.xfail(strict=True, reason='KNOWN (11 Nov 2026): columns of <= 8 cells give NaN in trace NH3 '
                   '(pnh3, 1e-50 atm boundary underflows) at the 2nd time step; production uses 15-25 cells')
def test_tiny_grid(model, nz):
    r, d = _run(model[0], [f'tiny{nz}', 'fe2o2,amo2o', '0.001', '--fallow', '--basalt=0'] + SOIL + [f'--nz={nz}', '--nstep=2'])
    assert sanity.check_run(d) == []

@pytest.mark.slow
def test_short_two_record_run(model):
    # shortest useful run on the smallest working grid: two output records, must finish clean
    r, d = _run(model[0], ['two', 'fe2o2,amo2o', '0.001', '--fallow', '--basalt=0'] + SOIL + ['--nz=10', '--nstep=2'])
    assert sanity.check_run(d) == []
