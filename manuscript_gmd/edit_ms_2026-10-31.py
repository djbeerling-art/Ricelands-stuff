import copy, datetime, sys
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
d = Document(SRC)
P = list(d.paragraphs)
AUTH, DATE = 'Claude', datetime.datetime(2026, 10, 31, 16, 30).strftime('%Y-%m-%dT%H:%M:%SZ')
_id = [9000]
log = []

def nid():
    _id[0] += 1; return str(_id[0])

def mk(tag):
    e = etree.SubElement(etree.Element('dummy'), qn(tag)); e.getparent().remove(e)
    return e

def run_with(src_r, text, deleted=False):
    r = copy.deepcopy(src_r)
    for c in list(r):
        if c.tag != qn('w:rPr'): r.remove(c)
    t = etree.SubElement(r, qn('w:delText' if deleted else 'w:t'))
    t.text = text; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return r

def wrap(kind, r):
    w = mk('w:' + kind); w.set(qn('w:id'), nid()); w.set(qn('w:author'), AUTH); w.set(qn('w:date'), DATE)
    w.append(r); return w

def first_run(p):
    rs = p._p.findall(qn('w:r'))
    return rs[0] if rs else etree.Element(qn('w:r'))

def sub(i, old, new, p=None):
    """Tracked replacement of `old` by `new` inside one run of paragraph i."""
    p = p if p is not None else P[i]
    for r in p._p.findall(qn('w:r')):
        ts = r.findall(qn('w:t'))
        if len(ts) != 1: continue
        txt = ts[0].text or ''
        k = txt.find(old)
        if k < 0: continue
        before, after = txt[:k], txt[k + len(old):]
        parent = r.getparent(); pos = parent.index(r)
        new_elems = []
        if before: new_elems.append(run_with(r, before))
        new_elems.append(wrap('del', run_with(r, old, deleted=True)))
        if new: new_elems.append(wrap('ins', run_with(r, new)))
        if after: new_elems.append(run_with(r, after))
        parent.remove(r)
        for j, e in enumerate(new_elems): parent.insert(pos + j, e)
        log.append(f'p{i}: "{old[:60]}" -> "{new[:60]}"'); return
    raise SystemExit(f'NOT FOUND p{i}: {old[:80]!r}')

def replace_all(i, new, p=None):
    p = p if p is not None else P[i]
    rs = p._p.findall(qn('w:r'))
    if not rs: raise SystemExit(f'no runs p{i}')
    proto = rs[0]
    for r in rs:
        txt = ''.join(t.text or '' for t in r.findall(qn('w:t')))
        pos = p._p.index(r)
        p._p.remove(r)
        p._p.insert(pos, wrap('del', run_with(r, txt, deleted=True)))
    p._p.append(wrap('ins', run_with(proto, new)))
    log.append(f'p{i}: rewritten')

def delete_par(i):
    p = P[i]
    for r in p._p.findall(qn('w:r')):
        txt = ''.join(t.text or '' for t in r.findall(qn('w:t')))
        pos = p._p.index(r); p._p.remove(r)
        p._p.insert(pos, wrap('del', run_with(r, txt, deleted=True)))
    pPr = p._p.get_or_add_pPr()
    rPr = pPr.find(qn('w:rPr'))
    if rPr is None: rPr = etree.SubElement(pPr, qn('w:rPr'))
    m = etree.SubElement(rPr, qn('w:del')); m.set(qn('w:id'), nid()); m.set(qn('w:author'), AUTH); m.set(qn('w:date'), DATE)
    log.append(f'p{i}: deleted')

def insert_after(i, text, like=None):
    src = P[like if like is not None else i]
    np_ = copy.deepcopy(src._p)
    for c in list(np_):
        if c.tag != qn('w:pPr'): np_.remove(c)
    pPr = np_.find(qn('w:pPr'))
    if pPr is None: pPr = etree.SubElement(np_, qn('w:pPr')); np_.insert(0, pPr)
    rPr = pPr.find(qn('w:rPr'))
    if rPr is None: rPr = etree.SubElement(pPr, qn('w:rPr'))
    for c in list(rPr): rPr.remove(c)
    m = etree.SubElement(rPr, qn('w:ins')); m.set(qn('w:id'), nid()); m.set(qn('w:author'), AUTH); m.set(qn('w:date'), DATE)
    np_.append(wrap('ins', run_with(first_run(src._p) if False else first_run(src), text)))
    P[i]._p.addnext(np_)
    log.append(f'after p{i}: inserted "{text[:60]}"')

def heading(i, new, style=None):
    replace_all(i, new)
    if style: P[i].style = d.styles[style]

# ---------------- edits ----------------
heading(0, 'Riceland SCEPTER v1.0: a reactive-transport model of flooded rice paddies for enhanced weathering, methane and nitrous oxide')

sub(10, 'calibrate it to IPCC emission factors (Sect. 3). We then test it against EW, slag and lime trials (Sect. 4), and show how its GHG and CO₂ removal responses vary with dose, site conditions, time and water management (Sect. 5).',
        'calibrate it to IPCC emission factors and test it against basalt, steel-slag and wollastonite trials (Sect. 3). We then show how its GHG and CO₂ removal responses vary with dose, site conditions and time (Sect. 4).')

sub(16, 'These settings describe the frozen v22 configuration; verify the final v23 configuration against its archived inputs.',
        'These settings are identical in v22 and v23 (Sect. 2.7).')
sub(19, 'should be given in the technical appendix.', 'are given in Appendix A.')
replace_all(20, 'Dissolved-phase conservation (schematic):')
sub(22, 'The full implementation and its units must be given before this equation is presented as the governing balance for exchangeable cations.',
        'Appendix A gives the full form and its units.')
sub(29, 'are required in Appendix A.', 'are given in Appendix A.')
sub(30, 'Implementation specification (GitHub, paddy/docs/riceland_process_spec.md, v15/v16): the reaction extent', 'In the implementation, the reaction extent')
sub(33, 'For each pathway, the applicable acceptor, substrate and inhibition factors must be tabulated explicitly, including',
        'Appendix A tabulates, for each pathway, the applicable acceptor, substrate and inhibition factors, including')
sub(38, 'Implementation specification: methanogenesis has rate R_CH4 = 1630 ×', 'In the implementation, methanogenesis has rate R_CH4 = 1860 ×')
sub(38, 'in the v16 calibration', 'in the v22 calibration')
sub(38, 'This formulation is transcribed from the process specification and requires a final line-by-line check against scepter.f90.',
        'This formulation matches the code in scepter.f90 (v22 and v23).')
sub(41, 'Implementation specification: the green-rust reaction is', 'The green-rust reaction is')
P[41].style = d.styles['Normal']
delete_par(48)   # thermodynamic verification note (point kept in the green-rust paragraph above)
delete_par(52)   # rate-law notation note (units go to Appendix A)
sub(57, 'must be specified in Appendix A.', 'are given in Appendix A.')
sub(67, 'Implementation specification: the Si feedback', 'The Si feedback')
sub(67, 'K_Si = 5 × 10⁻⁴ mol L⁻¹, [Si]ref = 2.7 × 10⁻⁴ mol L⁻¹ and w = 0.5', 'K_Si = 2 × 10⁻³ mol L⁻¹, [Si]ref = 2.7 × 10⁻⁴ mol L⁻¹ and w = 0.2')
replace_all(68, 'Plant transport and ebullition (Eqs. 8–9) are volumetric sinks distributed over the root zone and the saturated column, whereas floodwater exchange (Eq. 10) is a surface flux; the reported emissions are the depth integrals of the volumetric terms plus the surface flux.')
sub(70, 'with Si half-saturation 0.5 mmol L⁻¹, reference oxygen flux 3.65 mol O₂ m⁻² yr⁻¹ and fitted feedback strength w = 0.5.',
        'with Si half-saturation 2 mmol L⁻¹, reference oxygen flux 3.65 mol O₂ m⁻² yr⁻¹ and calibration-informed feedback strength w = 0.2.')
delete_par(72)   # water-saturation spec: moved to Sect. 2.6.2 (inserted after p76)
insert_after(76, 'Water saturation is imposed as S_w(z,t) = min[1, S_top(t) + (1 − S_top(t)) z/z_wt(t)] (Eq. 12). AWD drain–reflood cycles start after day 29. Percolation is a constant downward flux, so the hydrology is a prescribed forcing rather than a solved transient water balance.', like=76)
delete_par(77)   # code audit note (28 Oct)
sub(80, 'Hydrological scope: Equation (12)', 'Equation (12)')
sub(80, 'irrigation runoff. The paper should state that water-table and surface saturation histories are imposed management forcings.',
        'irrigation runoff: water-table and surface saturation histories are imposed management forcings.')
delete_par(82); delete_par(83)
sub(86, 'Second, 105 porewaters', 'Second, 175 porewaters')
sub(86, '+0.13 log units for calcite', '+0.14 log units for calcite')
sub(86, '0.15–0.26 units lower', '0.23–0.57 units lower')
sub(87, 'Eight verification cases are being rerun to test carbon closure. The effects of this correction on CH₄, N₂O, aqueous carbon chemistry and net GHG estimates must be quantified against v22 before the verification claim and numerical results are finalised.',
        'With v23, all eight verification runs close the carbon budget to within 3 × 10⁻¹⁴ of the gross flux in the reaction terms and 2 × 10⁻¹⁶ in storage, and Fe, N, Ca and Mg to within 5 × 10⁻¹¹ and 2 × 10⁻⁷ (Fig. 3d). At archetype irr061 in year 1, the fix changes CH₄, N₂O and potentially durable alkalinity export by less than 0.3 % and CO₂ degassing by up to 1 %, against a run-to-run reproducibility of about 0.1 %. The v22 results in Sects. 3.3 and 4 are therefore retained.')

heading(88, '3 Calibration and evaluation')
sub(95, 'comes out at 0.66–0.69, inside the IPCC range of 0.55–0.77.', 'comes out at 0.60–0.72 (four archetypes, year 1), inside the IPCC range of 0.55–0.77.')
heading(98, '3.3 Evaluation against amendment experiments', 'Heading 2')
sub(99, '(Table 1; Sect. 3)', '(Fig. 4)')
sub(104, 'are described in Sect. 3 and Sect. 2.7.', 'are described in Sects. 3.1–3.2 and 2.7.')
heading(105, '4 Model behaviour')
sub(106, 'All six archetype simulations are complete in v22. The v23 carbon-conservation correction is being evaluated against these results; figures and budgets remain explicitly labelled v22 until regression checks establish which calculations require replacement.',
         'The v23 carbon-closure fix changes year-1 CH₄, N₂O and alkalinity export by less than 0.3 % (Sect. 2.7), so these v22 results are retained.')
heading(108, '4.1 First-season and dose-response behaviour')
sub(109, ' The full dose-response and sensitivity datasets require alignment with the frozen v22 executable before quantitative ranges are retained here.', '')
heading(111, '4.2 Methane response and uncertainty in the empirical Si feedback')
heading(114, '4.3 Ten-year reference-site trajectories and methane-bridging sensitivity')
sub(115, 'In the warm rainfed archetype rf189 at 20 t ha⁻¹ yr⁻¹, the corresponding full and fixed-year-1 results are −26.3 and −21.6 t CO₂e ha⁻¹. The remaining archetypes will be inserted after their runs and budgets are checked.',
         'Across the six archetypes at 20 t ha⁻¹ yr⁻¹ (Fig. 8), the full and fixed-year-1 results are −26.3 and −21.6 (rf189), −35.8 and −25.9 (irr061), −16.9 and −24.2 (irr043), −22.6 and −21.0 (rf184), −69.3 and −31.1 (irr092) and −33.3 and −25.5 t CO₂e ha⁻¹ (rf151); area-weighted, −32.6 and −24.8 t CO₂e ha⁻¹. At irr043 the fixed-year-1 diagnostic gives the larger benefit, so it is not a conservative bound at every archetype.')
heading(117, '4.4 Water management and climate-metric interpretation')
heading(119, '5 Discussion')
heading(120, '5.1 Model advances and the separation of mineral weathering from inorganic carbon export')
heading(122, '5.2 Structural and mechanistic uncertainties')
heading(126, '5.3 Experiments needed to test the two-clock prediction')
heading(128, '5.4 Implications for enhanced-weathering assessment')
heading(130, '6 Conclusions')
sub(132, ' Net mitigation remains negative under both the full Fe-age-dependent model and a fixed-first-year-methane diagnostic (−32.0/−23.6 and −50.3/−40.5 t CO₂e ha⁻¹ at 10 and 20 t basalt ha⁻¹ yr⁻¹).', '')
replace_all(134, '[To be written from paddy/docs/riceland_process_spec.md, checked against scepter.f90 (v23). Include: rate laws and inhibition factors for each pathway (Eqs. 3–4); green-rust and Fe(II)-oxidation constants and units (Eqs. 5–6); gas-transport units (Eqs. 8–10); the input files written by the driver; and the model switches (driver flag → input file), moved here from Fig. 2.]')
sub(136, 'A carbon-conservation patch has been built as v23 but is not yet the validated basis for the reported results; commit identifier and regression outcomes will be added after verification.',
         'The verification in Fig. 3 used scepter_paddy_v23 (commit 267a856), which adds a nine-line carbon-closure fix to v22 with unchanged options and calibration; the fix changes CH₄, N₂O and alkalinity export by less than 0.3 % (Sect. 2.7).')

# figure captions (taken from the figures document)
replace_all(176, 'Fig. 1. Model structure and processes. (a) The 0.5 m paddy column (25 cells): puddled plough layer (0–0.2 m, mixed before each season), plough pan (0.20–0.24 m; aqueous and gas diffusivities × 0.1) and a partly saturated subsoil open to air at its base. CH₄ leaves by plant transport (30–90 % oxidised in the rhizosphere; Eqs. 8–9), ebullition (above 0.4 atm CH₄) and diffusion through the floodwater (Eq. 10). Percolation is 0.5 m yr⁻¹ (1.4 mm d⁻¹); Fe²⁺ leached through the pan is re-oxidised in the subsoil. Basalt, mixed into 0–0.15 m, releases cations, Fe²⁺, Si and alkalinity, and the model tracks three fates separately: cations retained on exchange sites and in porewater (CDR potential only), soil carbonate, and potentially durable alkalinity exported through the base (PDA = ALK − 2Fe(II) − 2NH₄⁺). The Si-dependent root-O₂ term (dashed box) is empirical and switchable (v22: K_Si = 2 mmol L⁻¹, w = 0.2; w = 0 switches it off). (b) Microbial electron-acceptor sequence (Monod kinetics in OM and acceptor, Eq. 3) and the Fe²⁺ cycle (green rust pH-stat, Eq. 5; siderite, FeS, exchange; re-oxidation by O₂ on drainage and in the fallow, Eq. 6). Urea hydrolyses to NH₄⁺, which is held on exchange sites, taken up by rice or nitrified to NO₃⁻; the N₂O yield of denitrification depends on pH (Eq. 7). NO₃⁻ inhibits pathways ③–⑤; goethite is reduced ~30× more slowly than ferrihydrite; CH₄ production is inhibited by reducible Fe(III) and SO₄²⁻ (Eq. 4). Microbial rates scale with Q10 = 2 (methanogenesis 3) from 25 °C (Eq. 2). pH is solved from charge balance at each Newton step, so reactions carry no explicit H⁺. (c) Seasonal saturation and drainage: a 113-day season (continuous flooding or AWD, both ending with a 14-day pre-harvest drain) and a 252-day drained fallow (water table 0.5 m), run as a chain of restarts. Tillage and basalt are applied on day 0; OM, Fe(III) and urea (120 kg N ha⁻¹) are added at a constant rate through the season.')
replace_all(177, 'Fig. 2. Implementation and simulation protocol. (a) Inputs, the Python driver, the original SCEPTER v1.0 core (grey) and the added paddy modules (green), and outputs. Each paddy term reads its own input file and is off when the file is absent. Frozen v22 provenance: executable, commit, calibrated constants and Si-feedback setting. (b) The run protocol: 3-yr drained spin-up, 7-yr settle without rock, then year-matched control and treatment chains from the same settled state (tillage, season, fallow), with GHG and CDR post-processing. The input files written by the driver and the model switches (driver flag → input file) are listed in Appendix A. Fig. 3 was rerun on v23 (v22 plus the carbon-closure fix).')
sub(178, ' Replace panel (d) and report verified residuals only after completion of the eight v23 reruns.', ' Panel (d) shows v23, which closes the carbon budget to machine precision.')
sub(179, 'basalt, steel slag and lime trials', 'basalt, steel-slag and wollastonite trials')
delete_par(184)  # revision status note

# Table 1
T = d.tables[0]
def cell(r, c): return T.rows[r].cells[c].paragraphs[0]
sub(-1, '1630', '1860', p=cell(1, 1))
sub(-1, '135 kg CH₄ per season', '130 kg CH₄ per season (year 1)', p=cell(1, 3))
sub(-1, '0.5', '0.2 (K_Si 2 mmol L⁻¹)', p=cell(9, 1))
replace_all(-1, 'Gong et al. (2026) basalt CH₄ −18 %; Wang et al. (2014) slag 2 t ha⁻¹ −27 %', p=cell(9, 2))
replace_all(-1, '−23 %; −35 %', p=cell(9, 3))
replace_all(-1, 'Na matched; Mg ~2× too fast (Sect. 3.3)', p=cell(10, 3))
replace_all(-1, 'control CH₄ still rises ~5 % yr⁻¹ (130 → 214 kg, years 1–10)', p=cell(11, 3))

d.save(OUT)
print('\n'.join(log)); print(len(log), 'edits')
