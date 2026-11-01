# Tracked edits on Riceland_SCEPTER_GMD_Nov1_v7.docx (David, 1 Nov 2026): (1) lateral floodwater export status,
# (2) charge-to-CO2 convention + calcite cap factor 1/2, (3) modelled vs verified removal, (4) v22 -> v25b numbers.
# Cyan = drafted interpretive/framing text for David to reword (GMD AI policy); yellow = flag, not rerun under v25b.
import re,sys,html,os,subprocess,tempfile
src,dst=sys.argv[1],sys.argv[2]
tmp=tempfile.mkdtemp(); subprocess.run(['unzip','-q',src,'-d',tmp],check=True)
P=os.path.join(tmp,'word/document.xml'); d=open(P,encoding='utf8').read()
DATE='2026-11-01T21:30:00Z'; AU='Claude'
ids=[int(x) for x in re.findall(r'w:id="(\d+)"',d)]; nid=[max(ids+[0])+5000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
TT=lambda r: ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',r))
def esc(s): return html.escape(s,quote=False)
def edit(ctx,old,new,hl=None,AT=None,n=None):
    global d
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if ectx in TT(m.group())]
    if n is None: assert len(hits)==1,(ctx,len(hits))
    m=hits[n or 0]; r=m.group(); assert r.count('<w:t')==1,ctx
    head=re.match(r'<w:r(?: [^>]*)?>',r).group()
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',r,re.S); rpr=rpr.group() if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',r,re.S); pre=r[len(head):tm.start()]
    text=tm.group(1)
    if old: assert esc(old) in ectx,(ctx,old)
    i=text.index(ectx)+ectx.index(esc(old)) if old else text.index(ectx)+(len(ectx) if AT is None else AT)
    before,after=text[:i],text[i+len(esc(old)):]
    T=lambda s:'<w:t xml:space="preserve">%s</w:t>'%s
    out=head+pre+T(before)+'</w:r>' if before else ''
    if old: out+='<w:del w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'%(wid(),AU,DATE,rpr,esc(old))
    if new:
        rp2=rpr
        if hl: rp2=rpr.replace('</w:rPr>','<w:highlight w:val="%s"/></w:rPr>'%hl) if rpr else '<w:rPr><w:highlight w:val="%s"/></w:rPr>'%hl
        out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins>'%(wid(),AU,DATE,rp2,T(esc(new)))
    if after: out+=head+rpr+T(after)+'</w:r>'
    d=d[:m.start()]+out+d[m.end():]
def flag(ctx,text,AT=None,n=None): edit(ctx,'',' ['+text+']','yellow',AT=AT,n=n)
def cyan(ctx,text,AT=None,n=None): edit(ctx,'',text,'cyan',AT=AT,n=n)

# ---------- Abstract (points 3, 4)
edit('reduced cumulative net greenhouse-gas emissions by 16.9–69.3','16.9–69.3','11.3–39.9')
edit('(area-weighted mean 32.6 t ','32.6','23.1')
edit('The mean benefit comprised CH₄ suppression (21.8 t ','21.8','11.7')
edit('exported alkalinity (2.1 t CO₂ ha⁻¹)','exported alkalinity (2.1','potentially durable alkalinity export (2.6')
edit('soil carbonate accumulation (7.2 t','7.2','7.6')
edit('and N₂O suppression (1.5 t ','1.5','1.2')
cyan(' ha⁻¹). After ten years, 73%',' The alkalinity and carbonate terms are modelled inorganic-carbon accounting terms, not verified atmospheric CO₂ removal: the model does not resolve their carbon source or long-term durability.',AT=len(' ha⁻¹).'))
edit('73% of weathering-released cations','73% of weathering-released cations','50% of the weathering-released cation charge')
edit('disabling it reduced the reference-site ten-year net benefit from approximately 50 to 38 t ','reference-site ten-year net benefit from approximately 50 to 38','reference-site ten-year net benefit at 20 t ha⁻¹ yr⁻¹ from 40.1 to 34.8')

# ---------- 2.4 / 2.3 parameters (v25b)
edit('R_CH4 = 1860 × g2','1860','2280')
edit('goethite at a first-order rate of 0.3 yr','0.3','0.1')
# ---------- 2.6.1 w = 0.15
edit('[Si]ref = 2.7 × 10⁻⁴ mol L⁻¹ and w = 0.2.','w = 0.2','w = 0.15')
edit('calibration-informed feedback strength w = 0.2','w = 0.2','w = 0.15')
edit('at which w = 0.2 implies a 40 % increase','w = 0.2 implies a 40 %','w = 0.15 implies a 30 %')
edit('reported with w = 0 alongside w = 0.2,','w = 0.2','w = 0.15')

# ---------- 2.6.2 lateral floodwater export (point 1)
edit(' Floodwater discharge is a constant prescribed rate while the surface is flooded.','',
 ' The lateral flux is a parameterised exchange, not a measured or simulated drainage flux. While the surface is flooded, the solute flux between the top cell and the floodwater is k_aq w_fw (C_top − C_irr), acting in series with diffusion across the upper half of the top cell, where C_top is the top-cell porewater concentration, C_irr the irrigation-water concentration at which the floodwater is renewed, and w_fw = min[1, max(0, (S_w,top − 0.9)/0.1)] the flooding weight also used for gas exchange (Eq. 10; Appendix A). k_aq is a scenario assumption: it is set so that 200 mm of floodwater is discharged per season (0.74 m yr⁻¹ of flooded time under continuous flooding and 0.96 m yr⁻¹ under AWD and the rainfed schedule; 100 and 400 mm as sensitivity cases), taken from the published range above and not fitted to discharge measured at any simulated site. The floodwater has no storage or water balance of its own: the discharged water is not withdrawn from the column, and percolation and the saturation profile stay as prescribed. The exchange conserves solute mass, because every mole leaving the top cell is counted as lateral export (Sect. 2.8), but the 200 mm water flux itself is notional.')

# ---------- 2.7 last sentence (point 4)
edit('The v22 results in Sects. 3.3 and 4 are therefore retained.','The v22 results in Sects. 3.3 and 4 are therefore retained.','Sects. 3.3 and 4 report simulations rerun with v25b (Sect. 2.8), which includes this fix.')

# ---------- 2.8 conventions (point 2)
edit(' per mol of charge; 1 mol m',' per mol of charge; 1 mol m',' m')
edit('Δ denotes basalt run minus the year-matched control from the same settled state.','',
 ' Cation release, alkalinity and PDA are counted in equivalents (mol of charge) and converted at 1 mol CO₂ per equivalent, the stoichiometry of charge balanced by bicarbonate (Ca²⁺ + 2HCO₃⁻: 2 eq, 2 mol CO₂; Na⁺ + HCO₃⁻: 1 eq, 1 mol CO₂). Net calcite precipitation is counted in mol CaCO₃ and converted at 1 mol CO₂ per mol (Ca²⁺ + 2HCO₃⁻ → CaCO₃ + CO₂ + H₂O), that is 0.5 mol CO₂ per equivalent of Ca²⁺; the calcite cap in Eq. (4) therefore uses half the remaining cation equivalents. The bicarbonate conversion is an upper bound for alkalinity that reaches the ocean, where re-equilibration with seawater carbonate chemistry retains about 0.8–0.85 mol CO₂ per equivalent (Renforth and Henderson, 2017); that factor is not applied here.')
edit('Realised CDR to year n, with net calcite precipitation C capped at the rock-derived cations not already exported:','',
 'Fe²⁺ and NH₄⁺ each count 2 eq because Fe²⁺ oxidation with Fe(OH)₃ precipitation, and nitrification of NH₄⁺, each release 2 H⁺ downstream. ',AT=0)
edit('Realised CDR to year n, with net calcite precipitation C capped at the rock-derived cations not already exported:','capped at the rock-derived cations not already exported:','capped at the calcite that the rock-derived cations not already exported could form (1 mol CaCO₃ per 2 eq):')
edit(' plant transport. Not counted: change in soil CO','',' ΔCH₄ and ΔN₂O in Eqs. (5)–(6) are treatment-minus-control emissions in t CH₄ and t N₂O ha⁻¹ (N₂O mass = N₂O-N × 44.01/28.01).',AT=len(' plant transport.'))
cyan('_*) where kept, otherwise summed output rates.',' ΔPDA and the capped calcite term are modelled inorganic-carbon terms, not verified atmospheric CO₂ removal: the model does not attribute the carbon in exported alkalinity or soil carbonate to an atmospheric, organic-matter or carbonate source, and PDA assumes complete downstream oxidation of Fe²⁺ and NH₄⁺ and no downstream degassing.')
# Eq. 4: insert tracked 1/2 before max(...) in the OMML
i=d.index('<m:t>CDR</m:t>'); j=d.index('<m:t>max</m:t>',i); k=d.rindex('<m:func>',i,j)
rr=re.search(r'<m:r>(<w:rPr>(?:(?!</w:rPr>).)*</w:rPr>)?<m:t>,</m:t></m:r>',d[i:j]); wrpr=(rr.group(1) or '') if rr else ''
mark='<w:ins w:id="%d" w:author="%s" w:date="%s"/>'%(wid(),AU,DATE)
wrpr=wrpr.replace('<w:rPr>','<w:rPr>'+mark,1) if wrpr else '<w:rPr>'+mark+'</w:rPr>'
d=d[:k]+'<m:r>'+wrpr+'<m:t>½</m:t></m:r>'+d[k:]

# ---------- 3.2 Table 1 (point 4)
flag('Table 1. Calibrated constants, the target each was tuned against, and the model result on the settled reference cycle.','Methanogenesis vmax, Si feedback and Fe(III) resupply rows updated to v25b; other model-result entries are v22 and need checking')
edit('1860 mol m⁻³ yr⁻¹','1860','2280',n=0)
edit('130 kg CH₄ per season (year 1)','130 kg CH₄ per season (year 1)','107 kg CH₄ per season (year 1; 0.95 kg ha⁻¹ d⁻¹, within the IPCC range 0.80–1.76)')
edit('0.2 (','0.2','0.15',n=0) if len([m for m in RUN.finditer(d) if TT(m.group())=='0.2 (']) else None
edit('slag 2 t ha⁻¹ −27 %','slag 2 t ha⁻¹ −27 %','slag 2, 4, 8 t ha⁻¹ −27, −43, −49 %')
edit('−23 %; −35 %','−23 %; −35 %','−36 %; −31, −38, −47 %')
edit('Na matched; Mg ~2× too fast','~2×','~1.7×')
edit('control CH₄ still rises ~5 % yr⁻¹ (130 → 214 kg','~5 % yr⁻¹ (130 → 214 kg','~1.8 % yr⁻¹ (107 → 126 kg')
flag('inside the IPCC range of 0.55–0.77.','v22 value; not rerun with v25b')

# ---------- 3.3 evaluation (point 4)
edit('The reference and archetype ten-year simulations use the frozen v22 executable;','The reference and archetype ten-year simulations use the frozen v22 executable;','The evaluation runs and the reference and archetype ten-year simulations use v25b;')
edit('% basalt; the model predicts 20% and 34%.','20% and 34%','15% and 26%')
edit('the revised shallow-mixing simulation predicts −23%','the revised shallow-mixing simulation predicts −23%','the v25b simulation (w = 0.15; P80 50 µm for the reported <75 µm powder) predicts −36%')
edit('modelled decreases are 35%, 43% and 52%.','35%, 43% and 52%','31%, 38% and 47%, with the slag simulated as the reported 1–7 mm granules')
flag('These mismatches restrict mechanistic attribution despite agreement in net CH₄ flux.','production/oxidation and ferric-Fe statements are from v22; check against v25b')
edit('but Mg release is 12.1 versus','12.1','11.0')
flag('without resolving the kinetic discrepancy independently.','v22 test')
edit('compared with model predictions of 0.31–0.48 over tested percolation rates.','model predictions of 0.31–0.48 over tested percolation rates','a v25b prediction of 0.10 t CO₂ ha⁻¹ (P80 50 µm for the reported ≤75 µm powder)')
flag('limits predicted carbonate accumulation.','v22 explanation; v25b not yet diagnosed')

# ---------- 4 intro
edit('We examine the frozen v22 reference-site','the frozen v22 reference-site','the v25b reference-site')
edit('The v23 carbon-closure fix changes year-1 CH₄, N₂O and alkalinity export by less than 0.3 % (Sect. 2.7), so these v22 results are retained.','The v23 carbon-closure fix changes year-1 CH₄, N₂O and alkalinity export by less than 0.3 % (Sect. 2.7), so these v22 results are retained.','All runs use v25b, which includes the v23 carbon-closure fix (Sect. 2.7) and the floodwater discharge of Sect. 2.6.2, with the year-round accounting of Sect. 2.8.')
# ---------- 4.1
edit('first-year annual CH₄ mitigation is 1.31 and 1.53','1.31 and 1.53','0.63 and 0.77')
edit('cation-release potentials are 2.48 and 4.60','2.48 and 4.60','2.55 and 4.72')
# ---------- 4.2
flag('the screen cannot validate the feedback mechanism.','v22 Morris screen; not yet rerun with v25b')
edit('Si-feedback strength from w = 0 to 0.2 and 0.4.','w = 0 to 0.2 and 0.4','w = 0 to 0.15 (reference) and 0.4')
edit('remains near 130–131 kg','130–131','107–109')
edit('approximately −2% at w = 0 to −37 to −44% at w = 0.2 and −59 to −66% at w = 0.4','approximately −2% at w = 0 to −37 to −44% at w = 0.2 and −59 to −66% at w = 0.4','+2 to +3% at w = 0 to −24 to −29% at w = 0.15 and −55 to −62% at w = 0.4')
edit(': −19/−38, −32/−50 and −42/−59 t ','−19/−38, −32/−50 and −42/−59','−16.1/−34.8, −21.6/−40.1 and −29.1/−47.0')
edit(' ha⁻¹ for w = 0, 0.2 and 0.4, respectively.','0.2','0.15')
flag('were identical across the four structures (Fig. 7).','v22 runs with w = 0.2; not rerun with v25b')
# ---------- 4.3
edit('net greenhouse-gas changes are −32.0 and −50.3 t ','−32.0 and −50.3','−21.6 and −40.1')
edit('are −23.6 and −40.5 t ','−23.6 and −40.5','−16.6 and −33.5')
edit('−26.3 and −21.6 (rf189), −35.8 and −25.9 (irr061), −16.9 and −24.2 (irr043), −22.6 and −21.0 (rf184), −69.3 and −31.1 (irr092) and −33.3 and −25.5','−26.3 and −21.6 (rf189), −35.8 and −25.9 (irr061), −16.9 and −24.2 (irr043), −22.6 and −21.0 (rf184), −69.3 and −31.1 (irr092) and −33.3 and −25.5','−23.6 and −19.2 (rf189), −23.5 and −16.6 (irr061), −11.3 and −5.2 (irr043), −21.6 and −20.7 (rf184), −39.9 and −21.2 (irr092) and −23.7 and −15.0')
edit('(rf151); area-weighted, −32.6 and −24.8 t ','−32.6 and −24.8','−23.1 and −16.1')
edit(' ha⁻¹. At irr043 the fixed-year-1 diagnostic gives the larger benefit, so it is not a conservative bound at every archetype.','At irr043 the fixed-year-1 diagnostic gives the larger benefit, so it is not a conservative bound at every archetype.','The fixed-year-1 diagnostic gives the smaller benefit at all six archetypes.')
edit('the first-year difference is 1.31 and 1.53','1.31 and 1.53','0.63 and 0.77')
edit('savings are 3.41/1.31 and 3.97/1.53','3.41/1.31 and 3.97/1.53','1.70/0.63 and 2.12/0.77')
edit('in year one to 1.88 and 3.54 t','1.88 and 3.54','1.98 and 3.95')
edit('becomes appreciable around years four to five,','around years four to five','around year five at 20 t ha⁻¹ yr⁻¹ and year seven at 10 t ha⁻¹ yr⁻¹')
edit('approximately year eight (10 t)','eight','six')
# ---------- 4.4
edit('require a fully matched v22 archetype comparison','v22','v25b')
edit('3.75E_CH₄(t−20)] × 32,','× 32','× 27 (GWP100 of CH₄, AR6)')
edit('warming-equivalent values of 102/62 and 119/73','102/62 and 119/73','45/25 and 57/31')
# ---------- 5.1
edit('occurs only after approximately four to five years, and 61–73% of released cations remain retained','approximately four to five years, and 61–73% of released cations remain retained','approximately five (20 t ha⁻¹ yr⁻¹) to seven (10 t ha⁻¹ yr⁻¹) years, and 37–59% of the released cation charge remains retained')
# ---------- 5.2
flag(' In an alternative structure in which dissolved Si lowers root CH₄ conductance','v22 runs',AT=0)
edit('from approximately 50 to 38 t ','approximately 50 to 38','40.1 to 34.8')
edit('the model lowers first-year CH₄ emission at the reference site by only about 2% (Fig. 6b)','lowers first-year CH₄ emission at the reference site by only about 2%','raises first-year CH₄ emission at the reference site by 2–3%')
flag('and raises first-year CH₄ production by about 12% (not ','v22 value',AT=len('and raises first-year CH₄ production by about 12%'))
flag('III) declines by approximately 1.1 mol m⁻² yr⁻¹, principally through downward ','v22 values in this paragraph; v25b ref control plough layer: ferrihydrite −0.54 and goethite −0.91 mol m⁻² yr⁻¹',AT=len('III) declines by approximately 1.1 mol m⁻² yr⁻¹'))
edit('in archetype irr043 it yields a larger mitigation benefit than the full trajectory.','in archetype irr043 it yields a larger mitigation benefit than the full trajectory.','in all six archetypes it yields a smaller mitigation benefit than the full trajectory (Sect. 4.3).')
# ---------- 5.4 / 6
edit('net GHG response, from −16.9 to −69.3 t ','−16.9 to −69.3','−11.3 to −39.9')
edit('). Their area-weighted mean of −32.6 t ','−32.6','−23.1')
edit('(−32.0/−23.6 and −50.3/−40.5 t ','−32.0/−23.6 and −50.3/−40.5','−21.6/−16.6 and −40.1/−33.5')
# ---------- Appendix A
edit('v = 1860 mol m⁻³ yr⁻¹ (calibrated); ','1860','2280')
edit('with k = 0.3 yr','0.3','0.1')
edit('--rtsi=2e-3:2.7e-4:0.2','--rtsi=2e-3:2.7e-4:0.2','--rtsi=2e-3:2.7e-4:0.15')
edit(' = 0.2 (',' = 0.2',' = 0.15')
flag('Values are those of the frozen production version: executable v22 (commit 162913','update provenance to v25b: executable scepter_paddy_v25, calibration paddy/krxn_calibrated_v25b.in, commit to add',AT=0)
flag('The reference and archetype analyses described here used the frozen scepter_paddy_v22','update code availability to v25b (executable, calibration file, options, commit)',AT=0)
# ---------- Captions
edit('switchable (v22: ','v22','v25b')
edit(' = 2 mmol L⁻¹, w = 0.2; w = 0 switches it off)','w = 0.2','w = 0.15')
edit('Frozen v22 provenance','Frozen v22','v25b')
edit('(Wang et al. 2014 at 2 t ha⁻¹ and Gong','2 t ha⁻¹','2, 4 and 8 t ha⁻¹')
edit('Mg release about 2× too fast','about 2×','about 1.7×')
edit('carbonate gain underpredicted 2.5–4×','2.5–4×','about 12×')
edit('reference site over 10 years (v22; each','v22;','v25b;')
edit('v22 reference (w = 0.2)','v22 reference (w = 0.2)','v25b reference (w = 0.15)')
edit('depends on w (130–131 kg','130–131','107–109')
edit('−2% with w = 0 against −37 to −44% (w = 0.2) and −59 to −66% (w = 0.4)','−2% with w = 0 against −37 to −44% (w = 0.2) and −59 to −66%','+2 to +3% with w = 0 against −24 to −29% (w = 0.15) and −55 to −62%')
edit('(to −36% at 10 t and −50% at 20 t','−36% at 10 t and −50%','−40% at 10 t and −54%')
edit('three cases: −19, −32 and −42 t ','−19, −32 and −42','−16, −22 and −29')
edit(' ha⁻¹ at 10 t ha⁻¹ yr⁻¹, and −38, −50 and −59 at 20 t ha⁻¹ yr⁻¹, for w = 0, 0.2 and 0.4.','−38, −50 and −59 at 20 t ha⁻¹ yr⁻¹, for w = 0, 0.2 and 0.4','−35, −40 and −47 at 20 t ha⁻¹ yr⁻¹, for w = 0, 0.15 and 0.4')
flag('Fig. 7. Alternative structures for the Si–root response at the reference site, 20 t basalt ha⁻¹ yr⁻¹ over ten years','v22 runs')
edit('after 10 years, 61–73% of the released cations are still retained in the soil.','61–73% of the released cations are','37–59% of the released cation charge (calcite counted as 2 eq per mol) is')
edit('Contrasting rice-soil archetypes: frozen v22,','frozen v22','v25b')
open(P,'w',encoding='utf8').write(d)
out=os.path.abspath(dst)
if os.path.exists(out): os.remove(out)
subprocess.run('cd %s && zip -q -r -X %s .'%(tmp,out),shell=True,check=True)
print('ok')
