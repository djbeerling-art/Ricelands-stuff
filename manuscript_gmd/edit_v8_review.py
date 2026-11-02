# Tracked edits on David's Nov1_v8_v25b (changes accepted): Mg clause + review table (1 Nov 21:07 UTC). Was: tracked edits on Riceland_SCEPTER_GMD_Nov1_v7.docx (David, 1 Nov 2026): (1) lateral floodwater export status,
# (2) charge-to-CO2 convention + calcite cap factor 1/2, (3) modelled vs verified removal, (4) v22 -> v25b numbers.
# Cyan = drafted interpretive/framing text for David to reword (GMD AI policy); yellow = flag, not rerun under v25b.
import re,sys,html,os,subprocess,tempfile
src,dst=sys.argv[1],sys.argv[2]
tmp=tempfile.mkdtemp(); subprocess.run(['unzip','-q',src,'-d',tmp],check=True)
P=os.path.join(tmp,'word/document.xml'); d=open(P,encoding='utf8').read()
DATE='2026-11-01T22:00:00Z'; AU='Claude'
ids=[int(x) for x in re.findall(r'w:id="(\d+)"',d)]; nid=[max(ids+[0])+5000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
TT=lambda r: ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',r))
def esc(s): return html.escape(s,quote=False)
def edit(ctx,old,new,hl=None,AT=None,n=None,exact=False):
    global d
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if (ectx==TT(m.group()) if exact else ectx in TT(m.group()))]
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

def delrange(c1,c2,newtext,hl=None):
    """tracked-delete all text runs from the run containing c1 to the run containing c2 (each unique), then insert newtext"""
    global d
    ms=list(RUN.finditer(d)); idx=lambda c:[i for i,m in enumerate(ms) if esc(c) in TT(m.group())]
    a,b=idx(c1),idx(c2); assert len(a)==1 and len(b)==1,(c1,a,c2,b); a,b=a[0],b[0]
    out=d[:ms[a].start()]
    for i in range(a,b+1):
        r=ms[i].group()
        if '<w:t' in r and TT(r):
            r2=re.sub(r'<w:t(?: [^>]*)?>','<w:delText xml:space="preserve">',r).replace('</w:t>','</w:delText>')
            out+='<w:del w:id="%d" w:author="%s" w:date="%s">%s</w:del>'%(wid(),AU,DATE,r2)
        else: out+=r
        out+=d[ms[i].end():ms[i+1].start()] if i<b else ''
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',ms[a].group(),re.S); rpr=rpr.group() if rpr else ''
    if hl: rpr=rpr.replace('</w:rPr>','<w:highlight w:val="%s"/></w:rPr>'%hl) if rpr else '<w:rPr><w:highlight w:val="%s"/></w:rPr>'%hl
    out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:ins>'%(wid(),AU,DATE,rpr,esc(newtext))
    d=out+d[ms[b].end():]
def drop(ctx): edit(ctx,ctx,'')

# ---- Review: 2.6.2 parameterised lateral solute-export boundary (David's wording + consistent terms)
edit('also exchange with floodwater that is continually renewed','also exchange with floodwater','are exported through a parameterised lateral solute-export boundary: they exchange with floodwater')
edit(' The lateral flux is a parameterised exchange, not a measured or simulated drainage flux.',' The lateral flux is a parameterised exchange, not a measured or simulated drainage flux.',
 ' Riceland SCEPTER v1.0 represents lateral solute export through a parameterised floodwater-exchange boundary. The prescribed exchange is scaled to seasonal discharge volumes but does not resolve floodwater storage, transient surface hydrology or the associated water balance. Consequently, lateral alkalinity export represents a scenario-dependent flux rather than a mechanistic prediction of drainage chemistry.')
edit('and by lateral floodwater discharge (fluxes J','by lateral floodwater discharge','through the lateral solute-export boundary of Sect. 2.6.2')
edit('the floodwater discharge of Sect. 2.6.2','the floodwater discharge of Sect. 2.6.2','the lateral solute-export boundary of Sect. 2.6.2')
# ---- Mg / charge-balance clause after Eq. 2 (David 21:03)
edit('Potentially durable alkalinity (2 ','',"ALK_base is the carbonate alkalinity given by the model's charge balance, so it includes the HCO₃⁻ that balances the Mg²⁺, Ca²⁺, Na⁺ and K⁺ released by weathering (for example Mg₂SiO₄ + 4CO₂ + 4H₂O → 2Mg²⁺ + 4HCO₃⁻ + H₄SiO₄, 2 mol CO₂ per Mg²⁺); the lateral term is the same charge balance written out. Mg²⁺ cannot form carbonate in the model (calcite is the only carbonate phase), so Mg-derived alkalinity is either exported or retained. ",AT=0)
# ---- 2.8 modelled vs atmospheric removal
edit('Realised CDR to year n, with net calcite precipitation C ','Realised CDR to year n','Modelled realised CDR to year n (an inorganic-carbon accounting term, not net atmospheric removal)')
# ---- 2.3 calibration label
edit(' = 1.0 in the v22 calibration.','v22','v25b')
# ---- Table 1 + AWD
drop(' [Methanogenesis vmax, Si feedback and Fe(III) resupply rows updated to v25b; other model-result entries are v22 and need checking]')
edit('the model result on the settled reference cycle.','',' Model results are v25b (reference control, year 1) except entries marked v22, which were not re-evaluated with v25b.')
edit('10–25 d','10–25 d','10–25 d (v22)')
edit('0–23%','0–23%','0–23% (v22)')
edit('0.47 at reference root-zone pH 5.5','0.47 at reference root-zone pH 5.5','0.47 at reference root-zone pH 5.5 (v22)')
edit('~11%','~11%','1.4 % (1.5 kg)')
edit('0.36 kg N₂O-N per season','0.36','0.31')
edit('0.3–0.9','0.3–0.9','0.8 kg N ha⁻¹ yr⁻¹',exact=True)
drop(' [v22 value; not rerun with v25b]')
edit('inside the IPCC range of 0.55–0.77.','',' These are v22 runs; the ratio was not re-evaluated with v25b.')
# ---- 3.3
edit('modelled oxidation declines, whereas','modelled oxidation declines','in v25b, modelled production falls by 22–29 % and soil-plus-rhizosphere oxidation by 19–21 % at 2–8 t ha⁻¹')
drop(' [production/oxidation and ferric-Fe statements are from v22; check against v25b]')
edit('is much larger than the simulated change.','',' (v22 comparison, not repeated with v25b)',AT=len('is much larger than the simulated change'))
drop(' [v22 test]')
edit('halving only its dissolution rate brings','halving only','in a v22 sensitivity test, halving only')
drop(' [v22 explanation; v25b not yet diagnosed]')
edit('limits predicted carbonate accumulation.','',' (diagnosed with v22; not yet re-examined with v25b)',AT=len('limits predicted carbonate accumulation'))
# ---- 4.2 Morris + historical structure tests + "must"
drop(' [v22 Morris screen; not yet rerun with v25b]')
edit('the screen cannot validate the feedback mechanism.','',' The screen was run with v22 (w = 0.2 calibration) and has not been repeated with v25b.')
drop(' [v22 runs with w = 0.2; not rerun with v25b]')
edit('An alternative structure (option --ch4si)','',"The following structural sensitivity tests are historical: they were run with v24 (v22 calibration, w = 0.2, no floodwater export or ferrihydrite ageing; Appendix A9) and have not been repeated with v25b, so their values are not directly comparable with the v25b results above. ",AT=0)
edit(' must therefore act by supplying O₂ to the root zone,',' must therefore act by supplying',' did so, among the four structures tested, only by supplying','cyan')
# ---- 5.2
# ---- 5.2 (historical v24 tests; Fe-decline numbers to v25b)
edit(' [v22 runs]',' [v22 runs]','',n=0)
edit('In an alternative structure in which dissolved Si lowers root CH₄ conductance','In an alternative structure','In historical v24 tests (Sect. 4.2) of an alternative structure')
drop(' [v22 value]')
edit(' (Fig. 6b) and raises first-year CH₄ production by about 12%','by about 12%','by about 12% in v22')
edit('III) declines by approximately 1.1 mol m⁻² yr⁻¹','approximately 1.1','approximately 1.45 (ferrihydrite 0.54, goethite 0.91)')
drop(' [v22 values in this paragraph; v25b ref control plough layer: ferrihydrite −0.54 and goethite −0.91 mol m⁻² yr⁻¹]')
edit('II) transport followed by subsoil reoxidation, while little Fe leaves the full column (Fig. 5f). The simulated decline in the initial reactive ','The simulated decline in the initial reactive ','The subsoil gains about the same amount (1.45 mol m⁻² yr⁻¹). The simulated decline in the initial plough-layer ')
edit('III) fraction is approximately 3.3% yr⁻¹, faster','III) fraction is approximately 3.3% yr⁻¹','III) inventory is approximately 1.7 % yr⁻¹ (ferrihydrite alone 1.2 % yr⁻¹)')
# ---- Appendix A intro, Table A8, A9 code versions, A9 table, A10, code availability
delrange(' [update provenance to v25b: executable scepter_paddy_v25, calibration paddy/krxn_calibrated_v25b.in, commit to add]',', and v23 (commit 267a856) for the verification in Fig. 3',
 'Values are those of the production version v25b: executable scepter_paddy_v25 (source commit 0f79804) with calibration file paddy/krxn_calibrated_v25b.in (commit b0ba34a) and w = 0.15. The verification in Fig. 3 used v23 (commit 267a856), the Morris screen in Fig. 6a v22 (commit 162913a, paddy/krxn_calibrated_v22.in) and the alternative Si–root structures in Fig. 7 v24 (commit f2d2aa8); version differences are listed in Sect. A9. Where the code default differs from the calibrated value, the calibrated value is given and the default is noted.')
edit('paddy/krxn_calibrated_v22.in','v22','v25b',n=0)
edit('1860 ','1860','2280')
delrange('Code versions: v22 (commit 162913a) produced Figs. ',' used for every run, and the run and post-processing scripts, so each figure can be regenerated with the version that produced it.',
 'Code versions: Sects. 3.3 and 4 and Figs. 4, 5, 6b, 8 and 9 use v25b: executable scepter_paddy_v25 built from commit 0f79804 (the production worktree, commit a8159b4, has the same model source) with calibration file paddy/krxn_calibrated_v25b.in (commit b0ba34a) and w = 0.15; budgets use paddy/ghg_budget.py at commit f96554d (time-integrated fluxes and the calcite cap of Eq. 4). Relative to v22 (commit 162913a, paddy/krxn_calibrated_v22.in, w = 0.2), v23 (commit 267a856) adds nine lines that return to CO₂ the 4 % of decomposed OM carbon that upstream SCEPTER routes to oxalate and acetate, which are not tracked in the paddy runs; this closes the carbon budget (Fig. 3) and changes CH₄, N₂O and alkalinity export by less than 0.3 % and CO₂ degassing by up to 1 % (irr061, year 1). v24 (commit f2d2aa8) adds the alternative Si–root-barrier structure (--ch4si; Sect. A5), used only for Fig. 7. v25 (commits 21e108f, 0402439 and 0f79804) adds Fe(II)-catalysed, Si-inhibited ferrihydrite ageing to goethite (fhage), raises goethite reduction (g2gt v_max 10 to 60 mol m⁻³ yr⁻¹) and adds the lateral solute-export boundary (--kaq); v25b sets the ageing rate to 0.1 yr⁻¹, methanogenesis v_max to 2280 mol m⁻³ yr⁻¹ and w to 0.15. Fig. 3 uses v23, Fig. 6a v22 and Fig. 7 v24; none of these three has been repeated with v25b. The archived release will contain each exact version with build instructions, its calibration file, the option strings (paddy/v25/stanage/pipeline_v25b.sbatch for the reference and archetype chains, paddy/v25/run_scripts for the evaluation runs) and the run and post-processing scripts, so each figure can be regenerated with the version that produced it.')
edit('krxn_calibrated_v22.in','v22','v25b',n=0)
edit('stanage_handoff/v22_options.env','stanage_handoff/v22_options.env','paddy/v25/stanage/pipeline_v25b.sbatch (variable PROD)')
delrange(' [update code availability to v25b (executable, calibration file, options, commit)]',' Fig. 7 used scepter_paddy_v24 (commit f2d2aa8), which adds the alternative Si–root-barrier option --ch4si to v23; the option is off in all other runs.',
 'The reference, archetype and evaluation simulations described here used v25b: the scepter_paddy_v25 executable built from commit 0f79804 with calibration file paddy/krxn_calibrated_v25b.in (commit b0ba34a), branch claude/project-thread-pip6bj-pan. The exact input files, scripts and figure datasets require archival with a persistent release DOI before submission [DOI pending]. The verification in Fig. 3 used scepter_paddy_v23 (commit 267a856), which adds a nine-line carbon-closure fix to v22; the Morris screen in Fig. 6a used scepter_paddy_v22 (commit 162913a); and Fig. 7 used scepter_paddy_v24 (commit f2d2aa8), which adds the alternative Si–root-barrier option --ch4si to v23. Figs. 6a and 7 have not been repeated with v25b (Appendix A9).')
# ---- Captions
edit(' [v22 runs]',' [v22 runs]','',n=0)
edit('Fig. 7. Alternative structures for the Si–root response at the reference site, 20 t basalt ha⁻¹ yr⁻¹ over ten years','',' (historical structural sensitivity test run with v24, v22 calibration; not repeated with v25b)')
edit('(w = 0.2, as in the main runs)','as in the main runs','as in the v22 main runs')
edit('split into potentially durable alkalinity exported at the column base (PDA','exported at the column base','exported at the column base and through the lateral solute-export boundary')
open(P,'w',encoding='utf8').write(d)
out=os.path.abspath(dst)
if os.path.exists(out): os.remove(out)
subprocess.run('cd %s && zip -q -r -X %s .'%(tmp,out),shell=True,check=True)
print('ok')
