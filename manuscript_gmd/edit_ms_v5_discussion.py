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
# ---- 5.1 ----
sub(120, 'Unlike an aerated-soil EW model, it represents the consequences of oxygen depletion, Fe and S transformations, rice-mediated gas transport and reoxidation during drainage within the same reactive-transport calculation.',
 'Unlike aerated-soil EW models (Kanzaki et al., 2022, 2024; Kelland et al., 2020), it represents the consequences of oxygen depletion, Fe and S transformations, rice-mediated gas transport and reoxidation during drainage within the same reactive-transport calculation, the sequence of redox processes that distinguishes submerged from upland soils (Ponnamperuma, 1972; Kirk, 2004; Kögel-Knabner et al., 2010). Existing paddy CH₄ models treat this sequence with empirical or lumped electron-acceptor terms (Huang et al., 2004; Fumoto et al., 2008); the kinetic redox cascade used here follows the general reaction-network approach of Van Cappellen and Wang (1996) and Hunter et al. (1998), and the explicit root CO₂ and O₂ terms follow Kirk et al. (2019).')
sub(121, 'Released base cations can remain in porewater or on exchange sites before contributing to exported alkalinity or secondary carbonate.',
 'Released base cations can remain in porewater or on exchange sites before contributing to exported alkalinity or secondary carbonate, a retention also reported in EW mesocosm and field studies on upland soils (Amann et al., 2020; Kelland et al., 2020; Beerling et al., 2024) and exploited by soil cation-budget methods for monitoring weathering (Reershemius et al., 2023).')
sub(121, 'These retained cations represent potential future inorganic carbon removal, not realised CDR.',
 'These retained cations represent potential future inorganic carbon removal, not realised CDR, in the sense that removal is completed only when alkalinity reaches a durable reservoir (Hartmann et al., 2013; Renforth and Henderson, 2017).')
sub(121, 'require independent field constraints.', 'require independent field constraints (Almaraz et al., 2022).')
sub(122, 'Avoided CH₄ emissions expressed using GWP100 or GWP* must remain distinct from physical CO₂ removal.',
 'Avoided CH₄ emissions expressed using GWP100 or GWP* (Allen et al., 2018) must remain distinct from physical CO₂ removal.')
# ---- 5.2 ----
sub(124, 'Its strength controls much of the first-year response, yet the model does not resolve changes in root anatomy, radial oxygen loss, rhizosphere oxidation or aerenchyma-mediated CH₄ transport independently.',
 'Its strength controls much of the first-year response, yet the model does not resolve changes in root anatomy, radial oxygen loss, rhizosphere oxidation or aerenchyma-mediated CH₄ transport independently. The physiological evidence for its direction is mixed (Sect. 2.6.1): slag silicate fertiliser raised root oxidase activity and methanotroph abundance (Das et al., 2022) and Si weakened the root barrier to radial O₂ loss under flooded conditions (Tong et al., 2024), whereas other studies found that Si strengthens that barrier (Fleck et al., 2011; Hinrichs et al., 2017), which also governs the entry of CH₄ into roots (Colmer, 2003).')
sub(125, 'Other processes, including mineral-derived Fe availability, pH changes and Fe redistribution, may contribute to the response. Mn cycling, microbial adaptation and pre-flooding residue decomposition are incompletely represented.',
 'Other processes, including mineral-derived Fe availability, pH changes and Fe redistribution, may contribute to the response: added Fe(III) oxides alone suppress paddy CH₄ (Jäckel and Schnell, 2000), slag trials attribute most of their effect to Fe-reducer competition with methanogens (Ali et al., 2008; Das et al., 2022), and Si applied without Fe has lowered, raised or left unchanged CH₄ emissions (Lou et al., 2019; Ku et al., 2020; Limmer et al., 2018), so part of the fitted plant response may stand in for Fe effects that the model under-represents (Sect. 3.3). Mn cycling, microbial community adaptation (Liesack et al., 2000; Conrad, 2007) and pre-flooding residue decomposition are incompletely represented.')
sub(126, 'Fe ageing is another consequential uncertainty.',
 'Fe ageing is another consequential uncertainty. Downward transport of Fe(II) and its reoxidation at depth is the classical mechanism of paddy-soil profile development, and chronosequences show progressive topsoil Fe loss over decades to centuries (Kirk, 2004; Kögel-Knabner et al., 2010; Kölbl et al., 2014; Huang et al., 2018).')
sub(126, 'Nevertheless, the difference matters because control CH₄ emissions rise as reducible Fe becomes depleted.',
 'Nevertheless, the difference matters because control CH₄ emissions rise as reducible Fe becomes depleted, in line with the dependence of methanogenesis on the supply of reducible Fe(III) (Roden and Zachara, 1996; Segers, 1998; Conrad, 2007).')
sub(128, 'Carbon fate depends on mineral-specific dissolution, exchangeable-cation retention, percolation and carbonate precipitation or dissolution.',
 'Carbon fate depends on mineral-specific dissolution, exchangeable-cation retention, percolation and carbonate precipitation or dissolution (Renforth and Henderson, 2017; Amann et al., 2020).')
# ---- 5.3 ----
sub(130, 'A decisive test would be a replicated, multi-season basalt-amendment experiment measuring CH₄ and inorganic carbon in the same paddies, including untreated controls, contrasting doses and matched water-management treatments.',
 'The available rice data are single-season field trials, pots or anoxic batches (Wang et al., 2014; Uchibayashi et al., 2025; Park et al., 2026; Gong et al., 2026) and agronomic-scale deployments without process measurements (Jordan et al., 2026). A decisive test would be a replicated, multi-season basalt-amendment experiment measuring CH₄ and inorganic carbon in the same paddies, including untreated controls, contrasting doses and matched water-management treatments, as in the multi-year EW trials on upland crops (Kelland et al., 2020; Beerling et al., 2024).')
sub(131, 'experiments should measure CH₄ production, oxidation and plant transport alongside porewater Si, root traits and radial oxygen loss.',
 'experiments should measure CH₄ production, oxidation and plant transport (Wang et al., 2014) alongside porewater Si, root oxidase activity (Das et al., 2022), root porosity and radial oxygen loss along individual roots, for which root-sleeving O₂ electrodes and methylene-blue staining are established methods (Colmer, 2003).')
sub(132, 'dissolved inorganic carbon and soil carbonate stocks are needed.',
 'dissolved inorganic carbon and soil carbonate stocks are needed (Almaraz et al., 2022; Reershemius et al., 2023).')
# ---- 5.4 ----
sub(134, 'rather than transferring assumptions from aerated soils.',
 'rather than transferring assumptions from aerated soils (Kanzaki et al., 2022; Kelland et al., 2020).')
sub(134, ' ha⁻¹ is a conditional scenario result for the sampled model configurations, not a regional forecast or a deployable removal factor.',
 ' ha⁻¹ is a conditional scenario result for the sampled model configurations, not a regional forecast or a deployable removal factor. The spread is of the same order as the site-to-site variation in paddy CH₄ emissions and in their response to management and silicate amendment reported by meta-analyses (Linquist et al., 2012; Lim et al., 2022).')
sub(135, 'whereas only the latter could qualify as CO₂ removal after appropriate source attribution and durability assessment.',
 'whereas only the latter could qualify as CO₂ removal after appropriate source attribution and durability assessment (Hartmann et al., 2013; Renforth and Henderson, 2017; Almaraz et al., 2022).')
sub(136, 'The framework can guide targeted field measurements and subsequent spatial assessments,',
 'The framework can guide targeted field measurements and subsequent spatial assessments of the kind made for upland croplands (Beerling et al., 2020),')
sub(136, 'Field evidence must precede claims about creditable methane suppression or durable carbon removal.',
 'Field evidence must precede claims about creditable methane suppression or durable carbon removal, as it does for EW on upland soils (Almaraz et al., 2022).')
# ---- references ----
new = [
 'Allen, M. R., Shine, K. P., Fuglestvedt, J. S., Millar, R. J., Cain, M., Frame, D. J., and Macey, A. H.: A solution to the misrepresentations of CO₂-equivalent emissions of short-lived climate pollutants under ambitious mitigation, npj Clim. Atmos. Sci., 1, 16, https://doi.org/10.1038/s41612-018-0026-8, 2018.',
 'Almaraz, M., Bingham, N. L., Holzer, I. O., Geoghegan, E. K., Goertzen, H., Sohng, J., and Houlton, B. Z.: Methods for determining the CO₂ removal capacity of enhanced weathering in agronomic settings, Front. Clim., 4, 970429, https://doi.org/10.3389/fclim.2022.970429, 2022.',
 'Amann, T., Hartmann, J., Struyf, E., de Oliveira Garcia, W., Fischer, E. K., Janssens, I., Meire, P., and Schoelynck, J.: Enhanced Weathering and related element fluxes – a cropland mesocosm approach, Biogeosciences, 17, 103–119, https://doi.org/10.5194/bg-17-103-2020, 2020.',
 'Beerling, D. J., Kantzas, E. P., Lomas, M. R., Taylor, L. L., Zhang, S., Kanzaki, Y., Eufrasio, R. M., Renforth, P., Mecure, J.-F., Pollitt, H., Holden, P. B., Edwards, N. R., Koh, L., Epihov, D. Z., Wolf-Gladrow, D. A., Hansen, J., and Banwart, S. A.: Enhanced weathering in the US Corn Belt delivers carbon removal with agronomic benefits, P. Natl. Acad. Sci. USA, 121, e2319436121, https://doi.org/10.1073/pnas.2319436121, 2024.',
 'Conrad, R.: Microbial ecology of methanogens and methanotrophs, Adv. Agron., 96, 1–63, https://doi.org/10.1016/S0065-2113(07)96005-8, 2007.',
 'Jäckel, U. and Schnell, S.: Suppression of methane emission from rice paddies by ferric iron fertilization, Soil Biol. Biochem., 32, 1811–1814, https://doi.org/10.1016/S0038-0717(00)00094-8, 2000.',
 'Kelland, M. E., Wade, P. W., Lewis, A. L., Taylor, L. L., Sarkar, B., Andrews, M. G., Lomas, M. R., Cotton, T. E. A., Kemp, S. J., James, R. H., Pearce, C. R., Hartley, S. E., Hodson, M. E., Leake, J. R., Banwart, S. A., and Beerling, D. J.: Increased yield and CO₂ sequestration potential with the C4 cereal Sorghum bicolor cultivated in basaltic rock dust-amended agricultural soil, Glob. Change Biol., 26, 3658–3676, https://doi.org/10.1111/gcb.15089, 2020.',
 'Kirk, G. J. D.: The Biogeochemistry of Submerged Soils, John Wiley & Sons, Chichester, 2004.',
 'Kögel-Knabner, I., Amelung, W., Cao, Z., Fiedler, S., Frenzel, P., Jahn, R., Kalbitz, K., Kölbl, A., and Schloter, M.: Biogeochemistry of paddy soils, Geoderma, 157, 1–14, https://doi.org/10.1016/j.geoderma.2010.03.009, 2010.',
 'Kölbl, A., Schad, P., Jahn, R., Amelung, W., Bannert, A., Cao, Z. H., Fiedler, S., Kalbitz, K., Lehndorff, E., Müller-Niggemann, C., Schloter, M., Schwark, L., Vogelsang, V., Wissing, L., and Kögel-Knabner, I.: Accelerated soil formation due to paddy management on marshlands (Zhejiang Province, China), Geoderma, 228–229, 67–89, https://doi.org/10.1016/j.geoderma.2013.09.005, 2014.',
 'Liesack, W., Schnell, S., and Revsbech, N. P.: Microbiology of flooded rice paddies, FEMS Microbiol. Rev., 24, 625–645, https://doi.org/10.1016/S0168-6445(00)00050-4, 2000.',
 'Linquist, B., van Groenigen, K. J., Adviento-Borbe, M. A., Pittelkow, C., and van Kessel, C.: An agronomic assessment of greenhouse gas emissions from major cereal crops, Glob. Change Biol., 18, 194–209, https://doi.org/10.1111/j.1365-2486.2011.02502.x, 2012.',
 'Reershemius, T., Kelland, M. E., Jordan, J. S., Davis, I. R., D\'Ascanio, R., Kalderon-Asael, B., Asael, D., Suhrhoff, T. J., Epihov, D. Z., Beerling, D. J., Reinhard, C. T., and Planavsky, N. J.: Initial validation of a soil-based mass-balance approach for empirical monitoring of enhanced rock weathering rates, Environ. Sci. Technol., 57, 19497–19507, https://doi.org/10.1021/acs.est.3c03609, 2023.',
 'Renforth, P. and Henderson, G.: Assessing ocean alkalinity for carbon sequestration, Rev. Geophys., 55, 636–674, https://doi.org/10.1002/2016RG000533, 2017.',
]
def key(t): return t.split(':')[0].lower().replace('ö','o').replace('ä','a').replace('š','s')
def before(name):
    end=min(i for i,p in enumerate(P) if i>155 and (p.text.startswith('Fig') or p.text.startswith('Table')))
    ents=[(i,p.text) for i,p in enumerate(P) if 155<i<end and p.text.strip()]
    prev=[i for i,t in ents if key(t) < key(name)]
    return prev[-1]
for txt_ in reversed(new):
    i=before(txt_); insert_after(i, txt_, like=156); log.append(f'  ({txt_[:20]} after: {P[i].text[:25]})')
d.save(OUT)
print('\n'.join(log))
