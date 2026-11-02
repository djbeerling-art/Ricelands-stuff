# Compare the irr061 year-1 check run on Stanage with the GMD v25b reference (paddy/v25/results/ghg_phase_rows.csv,
# set v25bb: same protocol, args from stanage_handoff/arch/archetypes_v22.csv).
# Usage (repo root): python3 stanage_handoff/compare_ref.py <run dir = $SCEPTER_OUT/paddy> [tag=g22_irr061]
# Pass = CH4, N2O, CO2 degassing and cation release within 1%; calcite and PDA within 0.1 t CO2/ha (nucleation noise).
import sys, csv
R = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else 'g22_irr061'
sys.argv = ['x', '--days=500']
exec(open('paddy/ghg_budget.py').read().split('ctrl = season')[0])
ref = {(int(r['dose_t_ha']), r['phase']): r for r in csv.DictReader(open('paddy/v25/results/ghg_phase_rows.csv'))
       if r['set'] == 'v25bb' and r['site'] == 'irr061' and r['year'] == '1'}
K = ['CH4 (kg/ha)', 'N2O (kg N/ha)', 'CO2 degassing (t/ha)', 'potentially durable ALK (t CO2/ha)', 'calcite (t CO2/ha)', 'cation release (t CO2/ha)']
bad = 0
for d in (0, 20):
    for x, ph in (('s', 'season'), ('f', 'fallow')):
        got = season(f'{R}/flood_{tag}_{d}_y1{x}'); r = ref[(d, ph)]
        for k in K:
            v, g = float(r[k]), got[k]
            if 'calcite' in k or 'ALK' in k: ok = abs(g-v) <= 0.1; dev = f'{g-v:+.3f} t'
            else: ok = abs(g-v) <= 0.01*abs(v) or abs(g-v) < 1e-3; dev = f'{100*(g/v-1) if v else 0:+.2f}%'
            bad += not ok
            print(f'{d:2d} t {ph:6s} {k:38s} ref {v:10.4f} stanage {g:10.4f} {dev:>10s} {"OK" if ok else "FAIL"}')
print('PASS' if bad == 0 else f'{bad} values outside tolerance')
