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
import re
# ---- Sect. 2.6.1 ----
replace_all(70, 'Silicate amendments lower paddy CH₄ emissions in most trials: by about 15 % in a meta-analysis of slag-based silicate fertiliser (Lim et al., 2022) and by 12–33 % in pot and field experiments with slag at 2–20 Mg ha⁻¹ (Ali et al., 2008; Das et al., 2022; Wang et al., 2014). Slag supplies Fe(III) as well as Si, and the Fe electron-acceptor pathway, which the model represents explicitly (Sect. 2.4), is the mechanism these studies rank first (Ali et al., 2008; Das et al., 2022). A plant-mediated contribution is also reported: with slag silicate fertiliser at 2 Mg ha⁻¹, root oxidase activity, soil CH₄-oxidation potential and methanotroph abundance increased, and structural equation modelling linked dissolved Si to CH₄ suppression through root oxidase activity (Das et al., 2022); Si-amended roots also had higher porosity (Ali et al., 2008); and under stagnant, flooding-like conditions Si delayed and weakened the barrier to radial O₂ loss in rice roots (Tong et al., 2024), consistent with the greater root oxidising power long reported for Si-fed rice (Okuda and Takahashi, 1965; Ma and Takahashi, 2002). The model represents this plant response with an empirical feedback that scales the prescribed root O₂ release by porewater Si relative to a reference value (0.27 mmol L⁻¹), with Si half-saturation 2 mmol L⁻¹, reference O₂ flux 3.65 mol O₂ m⁻² yr⁻¹ and calibration-informed feedback strength w = 0.2. Setting w = 0 removes the feedback and isolates the simulated geochemical contribution.')
replace_all(73, 'The direction of this term is contested. Other studies found that Si enhances exodermal suberisation and lignification and strengthens the barrier to radial O₂ loss (Fleck et al., 2011; Hinrichs et al., 2017), which would reduce O₂ loss per unit root surface; the same barrier also restricts the entry of soil gases such as CH₄ into roots, so Si could alter plant-mediated emission through root gas conductance rather than O₂ supply (Colmer, 2003); Si reduced inducible aerenchyma in the same experiment that found a weaker barrier (Tong et al., 2024); and Si applied without Fe has lowered, raised or left unchanged paddy CH₄ emissions (Lou et al., 2019; Ku et al., 2020; Limmer et al., 2018). The O₂ scaling is therefore an empirical proxy for the net plant response to silicate amendment, not a resolved mechanism. Two independent checks support its parameters: the reference value of 0.27 mmol L⁻¹ matches the upper end of porewater Si in unamended paddy soil (0.05–0.26 mmol L⁻¹), and amended porewater reaches about 1.1 mmol L⁻¹ (Das et al., 2022), at which w = 0.2 implies a 40 % increase in root O₂ release. Because the calibration targets (Gong et al., 2026; Wang et al., 2014) involve amendments that supply Fe as well as Si, w may partly compensate for Fe(III) effects that the model under-represents (Sect. 3.3).')
insert_after(73, 'The feedback is treated as a structural uncertainty. Every headline result is reported with w = 0 alongside w = 0.2, and Sect. 4.x tests an alternative structure in which dissolved Si lowers root gas conductance instead of raising O₂ release, calibrated to the same first-year CH₄ response.', like=73)

# ---- references (inserted after the alphabetically preceding entry) ----
refs = [
 ('Akiyama, H.', 'Ali, M. A., Lee, C. H., and Kim, P. J.: Effect of silicate fertilizer on reducing methane emission during rice cultivation, Biol. Fertil. Soils, 44, 597–604, https://doi.org/10.1007/s00374-007-0243-5, 2008.'),
 ('Bourrié, G.', 'Das, S., Jena, S. N., Bhuiyan, M. S. I., Kim, G. W., and Kim, P. J.: Mechanism of slag-based silicate fertilizer suppressing methane emissions from paddies, J. Clean. Prod., 373, 133799, https://doi.org/10.1016/j.jclepro.2022.133799, 2022.'),
 ('Bourrié, G.', 'Colmer, T. D.: Long-distance transport of gases in plants: a perspective on internal aeration and radial oxygen loss from roots, Plant Cell Environ., 26, 17–36, https://doi.org/10.1046/j.1365-3040.2003.00846.x, 2003.'),
 ('Hartmann, J., West', 'Hinrichs, M., Fleck, A. T., Biedermann, E., Ngo, N. S., Schreiber, L., and Schenk, M. K.: An ABC transporter is involved in the silicon-induced formation of Casparian bands in the exodermis of rice, Front. Plant Sci., 8, 671, https://doi.org/10.3389/fpls.2017.00671, 2017.'),
]
def idx(prefix):
    c=[i for i,p in enumerate(P) if i>154 and p.text.startswith(prefix)]
    assert len(c)==1, (prefix,c); return c[0]
for pre,txt in refs: insert_after(idx(pre), txt, like=155)
# entries whose predecessor must be found from the list
def before(name):
    # last existing reference entry alphabetically before `name`
    end=min(i for i,p in enumerate(P) if i>154 and (p.text.startswith('Fig') or p.text.startswith('Table')))
    ents=[(i,p.text) for i,p in enumerate(P) if 154<i<end and p.text.strip()]
    prev=[i for i,t in ents if t.split(':')[0].lower() < name.lower()]
    return prev[-1]
late = [
 ('Ku, H. H.', 'Ku, H. H., Hayashi, K., Agbisit, R., and Villegas-Pangga, G.: Effects of calcium silicate on nutrient use of lowland rice and greenhouse gas emission from paddy soil in the Philippines under alternating wetting and drying, Pedosphere, 30, 535–543, 2020.'),
 ('Lim, J. Y.', 'Lim, J. Y., Kang, Y. G., Sohn, K. M., Kim, P. J., and Galgo, S. J. C.: Creating new value of blast furnace slag as soil amendment to mitigate methane emission and improve rice cropping environments, Sci. Total Environ., 806, 150961, 2022.'),
 ('Limmer, M. A.', 'Limmer, M. A., Mann, J., Amaral, D. C., Vargas, R., and Seyfferth, A. L.: Silicon-rich amendments in rice paddies: effects on arsenic uptake and biogeochemistry, Sci. Total Environ., 624, 1360–1368, 2018.'),
 ('Lou, Y.', 'Lou, Y., Ren, L., Zhao, S., Shi, Y., Zhang, Y., and Zhu, H.: Effects of silicate application on CH₄ and N₂O emissions and global warming potentials in paddy soil under enhanced UV-B radiation, Energy Sci. Eng., 7, 1784–1794, 2019.'),
 ('Ma, J. F. and Takahashi', 'Ma, J. F. and Takahashi, E.: Soil, Fertilizer, and Plant Silicon Research in Japan, Elsevier, Amsterdam, 2002.'),
 ('Okuda, A.', 'Okuda, A. and Takahashi, E.: The role of silicon, in: The Mineral Nutrition of the Rice Plant, Johns Hopkins Press, Baltimore, 123–146, 1965.'),
 ('Tong, S.', 'Tong, S., Ranathunge, K., Pellegrini, E., Liu, D., Herzog, M., Jiménez, J. de la C., Kotula, L., and Pedersen, O.: Silicon weakens the outer apoplastic barrier in roots of rice and delays its formation, resulting in increased Na⁺ and Cl⁻ fluxes to the shoot, Environ. Exp. Bot., 105941, https://doi.org/10.1016/j.envexpbot.2024.105941, 2024.'),
]
# insert in reverse so that several entries after the same predecessor keep alphabetical order
for name,txt in reversed(late):
    i=before(name); insert_after(i, txt, like=155); log.append(f'  ({name} after p{i}: {P[i].text[:30]})')
d.save(OUT)
print('\n'.join(log))
