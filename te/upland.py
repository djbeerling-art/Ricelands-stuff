"""Upland (aerated cropland) SCEPTER driver for the trace-element (TE) study.

Spin-up follows the upstream GMD24 inert-soil approach (inert matrix + OM + CEC,
Ca rain and N fertiliser setting soil pH), then basalt is applied as dust.
"""
import os, sys, shutil, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import make_inputs as mi

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXE = os.path.join(ROOT, 'scepter_gmd24')
OUT = os.environ.get('TE_OUT', '/home/user/te_runs/')


def write_common(run, *, ztot=0.5, nz=30, ttot, temp, fdust=0., taudust=0.,
                 omrain, poro, moist, q, w, zdust=0.2, restart='false',
                 rstrt='self', mix=1, cec, alpha=3.4, ca_rain, n_rain,
                 sld=None, dust=None, psd=True, nstep=10):
    mi.get_input_frame(outdir=OUT, runname=run, ztot=ztot, nz=nz, ttot=ttot,
                       temp=temp, fdust=fdust, fdust2=0, taudust=taudust,
                       omrain=omrain, zom=ztot, poro=poro, moistsrf=moist,
                       zwater=100000, zdust=zdust, w=w, q=q, p=10e-6,
                       nstep=nstep, rstrt=rstrt, runid=run)
    mi.get_input_switches(outdir=OUT, runname=run, w_scheme=1, mix_scheme=mix,
                          poro_iter='false', sldmin_lim='true', display=1,
                          report=0, restart=restart, rough='true',
                          act_ON='false', dt_fix='false', cec_on='true',
                          dz_fix='true', close_aq='false', poro_evol='true',
                          sa_evol_1='true', sa_evol_2='false',
                          psd_bulk='true' if psd else 'false',
                          psd_full='true' if psd else 'false', season='false')
    sld_list = ['inrt', 'g2', 'amnt'] + (sld or [])
    aq_list = ['ca', 'k', 'mg', 'na', 'no3']
    if sld:
        aq_list += ['si', 'al', 'fe2', 'fe3']
    mi.get_input_tracers(outdir=OUT, runname=run, sld_list=sld_list,
                         aq_list=aq_list, gas_list=['pco2', 'po2'] if sld else ['pco2'],
                         exrxn_list=['fe2o2'] if sld else [])
    rain = [('ca', ca_rain)] + [(sp, 1e-20) for sp in aq_list
                                     if sp not in ('ca', 'fe3')]
    if sld:
        rain += [('fe3', 1e-21)]
    mi.get_input_tracer_bounds(outdir=OUT, runname=run, pr_list=[('inrt', 1.0)],
                               rain_list=rain)
    mi.get_input_sld_properties(outdir=OUT, runname=run, filename='dust.in',
                                sld_varlist=dust or [])
    mi.get_input_sld_properties(outdir=OUT, runname=run, filename='cec.in',
                                sld_varlist=[(sp, cec, 5.9, 4.8, 10.47, 10.786, 16.47, alpha)
                                             for sp in ('inrt', 'g2')])
    # N fertiliser as NH4NO3 normalised to OC rain (as GMD24)
    nr = n_rain / 14. * 80. / 2. / omrain
    mi.get_input_sld_properties(outdir=OUT, runname=run, filename='OM_rain.in',
                                sld_varlist=[('g2', 1), ('amnt', nr)])
    mi.get_input_sld_properties(outdir=OUT, runname=run, filename='2ndslds.in',
                                srcfile=os.path.join(ROOT, 'data/2ndslds_def.in'))
    mi.get_input_sld_properties(outdir=OUT, runname=run, filename='psdrain.in',
                                srcfile=os.path.join(ROOT, 'data/psdrain_100um.in'))
    shutil.copy(EXE, os.path.join(OUT, run, 'scepter'))


def run(run):
    d = os.path.join(OUT, run)
    return os.system(f'cd {d} && ./scepter > log.txt 2>&1')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--ttot', type=float, default=10000)
    ap.add_argument('--temp', type=float, default=10)
    ap.add_argument('--q', type=float, default=0.25)
    ap.add_argument('--w', type=float, default=1e-3)
    ap.add_argument('--moist', type=float, default=0.5)
    ap.add_argument('--cec', type=float, default=12)
    ap.add_argument('--om', type=float, default=300)
    ap.add_argument('--ca', type=float, default=5e-6)
    ap.add_argument('--n', type=float, default=15)  # g N/m2/yr
    a = ap.parse_args()
    write_common(a.name, ttot=a.ttot, temp=a.temp, omrain=a.om, poro=0.5,
                 moist=a.moist, q=a.q, w=a.w, cec=a.cec, ca_rain=a.ca,
                 n_rain=a.n)
    print('rc', run(a.name))


ROCKS = {  # SCEPTER mineral recipes (wt fraction)
    'hillhouse': [('la', 0.346), ('agt', 0.327), ('fo', 0.147), ('anl', 0.071)],
    # Pioneer Valley metabasalt (Vermont trial, Zacharias et al.): plagioclase +
    # clinopyroxene with chlorite as the main alteration phase, no olivine.
    # Approximate split from the XRD description; the rest is treated as inert.
    'pioneer': [('la', 0.45), ('agt', 0.30), ('clch', 0.08)],
}
SECONDARY = ['ka', 'gb', 'amsi', 'gt', 'cc']


def amend(spin, name, *, rock='hillhouse', dose=40., years=40., temp, q, moist,
          cec, ca_rain, omrain=300, w=0., zdust=0.2, nstep=10, pulse=None):
    """Restart from spin-up and apply rock continuously at dose t/ha/yr, or,
    with pulse = tau (yr, < 1), once: dose t/ha spread over the first tau years."""
    d = os.path.join(OUT, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    shutil.copytree(os.path.join(OUT, spin), d)
    for sub in ('flx',):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    minerals = [m for m, _ in ROCKS[rock]] if dose > 0 else []
    write_common(name, ttot=years, temp=temp, fdust=dose * 100.,
                 taudust=pulse if pulse else years,
                 omrain=omrain, poro=0.5, moist=moist, q=q, w=w, zdust=zdust,
                 restart='true', rstrt=os.path.join(OUT, spin), mix=3, cec=cec, ca_rain=ca_rain,
                 n_rain=0., sld=minerals + SECONDARY, dust=ROCKS[rock] if dose > 0 else [],
                 nstep=nstep)
    return run(name)
