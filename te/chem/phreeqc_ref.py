"""Run the same batch problems in PHREEQC (IPhreeqc via phreeqpython).

Each case fixes pH (Fix_H+ with NaOH), optionally pe (Fix_pe with O2(g)) and
pCO2 (CO2(g)), and equilibrates a solution with an exchanger, Hfo surface and
optional minerals. PHREEQC's system totals after the acid/base additions are
returned so the Python solver can be driven with exactly the same inputs.
"""
import os

from phreeqpython.viphreeqc import VIPhreeqc

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'data', 'minteq.v4.dat')
EXTRA = os.path.join(HERE, 'data', 'te_extra.dat')


def _ip():
    ip = VIPhreeqc()
    ip.load_database(DB)
    return ip


def run(case, species):
    """case: dict with T (C), W (kg), solution {label: mol/kgw}, pH list,
    pe (or None; fixed with Fix_pe), o2_si (or None; pe from O2(g) instead),
    pco2_si (or None), cec (mol), hfo (dict weak, strong, mass,
    area) or None, minerals list, elements list (for SYS output).
    species: aqueous + exchange + surface species names to punch.
    Returns a list of dict rows, one per pH."""
    extra = open(EXTRA).read()
    sol = '\n'.join(f'  {k} {v}' for k, v in case['solution'].items())
    lines = [extra, 'SOLUTION 1', f"  temp {case.get('T', 25)}", '  units mol/kgw',
             f"  -water {case.get('W', 1.0)}", '  pH 3.0', sol]
    if case.get('pe') is not None:
        lines.append(f"  pe {case['pe']}")
    lines.append('END')
    names = ['pH', 'pe', 'mu', 'W']
    els = case['elements']
    punch = ['10 PUNCH -LA("H+"), -LA("e-"), MU, TOT("water")']
    ln = 20
    for e in els:
        punch.append(f'{ln} PUNCH SYS("{e}")')
        names.append('SYS_' + e)
        ln += 1
    for sp in species:
        punch.append(f'{ln} PUNCH MOL("{sp}"), LG("{sp}")')
        names += ['MOL_' + sp, 'LG_' + sp]
        ln += 1
    for m in case.get('minerals', []):
        punch.append(f'{ln} PUNCH EQUI("{m}")')
        names.append('EQUI_' + m)
        ln += 1
    head = ' '.join(f'"{n}"' for n in names)
    rows = []
    for pH in case['pH']:
        b = list(lines)
        b += ['USE SOLUTION 1', 'EQUILIBRIUM_PHASES 1',
              f'  Fix_H+ {-pH} NaOH 10']
        if case.get('o2_si') is not None:
            b.append(f"  O2(g) {case['o2_si']} 10")
        elif case.get('pe') is not None:
            b.append(f"  Fix_pe {-case['pe']} O2(g) 10")
        if case.get('pco2_si') is not None:
            b.append(f"  CO2(g) {case['pco2_si']} 10")
        for m in case.get('minerals', []):
            b.append(f'  {m} 0 0')
        if case.get('cec'):
            b += ['EXCHANGE 1', f"  X {case['cec']}", '  -equilibrate 1']
        if case.get('hfo'):
            h = case['hfo']
            b += ['SURFACE 1', f"  Hfo_wOH {h['weak']} {h['area']} {h['mass']}",
                  f"  Hfo_sOH {h['strong']}", '  -equilibrate 1']
        b += ['USER_PUNCH', '-headings ' + head] + punch + \
             ['SELECTED_OUTPUT', '-reset false', 'END']
        ip = _ip()
        ip.run_string('\n'.join(b))
        arr = ip.get_selected_output_array()
        row = dict(zip(names, arr[-1]))
        rows.append(row)
    return rows
