# Tracked edits to David's Riceland_SCEPTER_GMD_Nov1.docx (document.xml in cwd): 2.6.1 pointer, Sect. 4.2 conductance
# results + interpretation draft, new Fig. 7 placeholder with renumbering, GWP* re-cited to Allen/Cain.
import re
p='word/document.xml'; s=open(p).read()
D='w:author="Claude" w:date="2026-11-01T07:20:00Z"'
nid=[9400]
def I(): nid[0]+=1; return nid[0]
RUN=r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>'
def rpr_of(run):
    m=re.search(r'<w:rPr>(?:(?!</w:r>).)*?</w:rPr>',run); return m.group(0) if m else ''
# 1. 2.6.1 pointer
m=[x for x in re.finditer(RUN,s) if 'Sect. 4.x' in x.group(0)][0]
run=m.group(0); rpr=rpr_of(run); txt=re.search(r'<w:t[^>]*>(.*)</w:t>',run).group(1)
pre,post=txt.split('Sect. 4.x',1); tail=', calibrated to the same first-year CH₄ response.'; assert post.endswith(tail); core=post[:-len(tail)]
new=(f'<w:r>{rpr}<w:t xml:space="preserve">{pre}Sect. 4.</w:t></w:r><w:del w:id="{I()}" {D}><w:r>{rpr}<w:delText>x</w:delText></w:r></w:del>'
 f'<w:ins w:id="{I()}" {D}><w:r>{rpr}<w:t>2</w:t></w:r></w:ins><w:r>{rpr}<w:t xml:space="preserve">{core}</w:t></w:r>'
 f'<w:del w:id="{I()}" {D}><w:r>{rpr}<w:delText xml:space="preserve">, calibrated to the same first-year CH₄ response</w:delText></w:r></w:del><w:r>{rpr}<w:t>.</w:t></w:r>')
s=s[:m.start()]+new+s[m.end():]
# 2. figure renumbering 7->8, 8->9 (before adding the new Fig. 7 text)
def fix_run(mm):
    run=mm.group(0); tm=re.search(r'<w:t[^>]*>([^<]*)</w:t>',run)
    if not tm or not re.search(r'Figs?\. [78]',tm.group(1)): return run
    txt=tm.group(1); rpr=rpr_of(run); out=''; pos=0
    for f in re.finditer(r'(Figs?\. )([78](?:–[78])?)',txt):
        out+=f'<w:r>{rpr}<w:t xml:space="preserve">{txt[pos:f.start(2)]}</w:t></w:r>'
        old=f.group(2); newd=''.join({'7':'8','8':'9'}.get(c,c) for c in old)
        out+=f'<w:del w:id="{I()}" {D}><w:r>{rpr}<w:delText>{old}</w:delText></w:r></w:del><w:ins w:id="{I()}" {D}><w:r>{rpr}<w:t>{newd}</w:t></w:r></w:ins>'
        pos=f.end(2)
    return out+f'<w:r>{rpr}<w:t xml:space="preserve">{txt[pos:]}</w:t></w:r>'
s=re.sub(RUN,fix_run,s)
# 3. Sect. 4.2 results + interpretation after the Fig. 6b paragraph
j=s.find('These comparisons do not independently validate the Si–root-O₂ mechanism.'); pe=s.find('</w:p>',j)+6
pstart=s.rfind('<w:p ',0,j); ppr=re.search(r'<w:pPr>.*?</w:pPr>',s[pstart:pe]).group(0)
def pp(base):
    n=I(); return base.replace('<w:rPr>',f'<w:rPr><w:ins w:id="{n}" {D}/>',1) if '<w:rPr>' in base else base.replace('</w:pPr>',f'<w:rPr><w:ins w:id="{n}" {D}/></w:rPr></w:pPr>')
R='<w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
RS='<w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:vertAlign w:val="subscript"/></w:rPr>'
RH='<w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:highlight w:val="cyan"/></w:rPr>'
segs=[("An alternative structure (option --ch4si) scales plant CH₄ conductance and the rhizosphere oxidation of plant-transported CH₄ by 1/b, with b = 1 − w",0),("c",1),(" + w",0),("c",1),(" h([Si])/h([Si]",0),("ref",1),(") and the same h, K",0),("Si",1),(" and [Si]",0),("ref",1),(" as the O₂ term, so that rising Si lowers conductance when w",0),("c",1),(" > 0. At the reference site with 20 t basalt ha⁻¹ yr⁻¹, w",0),("c",1),(" = 0.5 and no O₂ term, first-year CH₄ emission increased by 60 % relative to the matched control (216 vs 135 kg ha⁻¹), and by 73 % in year 3. Plant-mediated emission fell from 120 to 67 kg ha⁻¹, but ebullition rose from 11 to 137 kg ha⁻¹ and floodwater diffusion from 4.5 to 12 kg ha⁻¹, so that about 2.5 kg CH₄ was emitted by other pathways for each kilogram removed from plant transport. In year 10, ebullition was 207 kg ha⁻¹, against 33 kg ha⁻¹ in the control. Lowering conductance therefore increased emission at the strength tested, and this structure did not reproduce the observed first-year decrease. Ten-year net realised GHG change was −3.2 t CO₂e ha⁻¹, compared with −50.0 t CO₂e ha⁻¹ for the O₂ structure (w = 0.2). Applying the same barrier to root O₂ release as well (w",0),("r",1),(" = 0.5) gave +30.0 t CO₂e ha⁻¹, whereas a leakier barrier combined with the O₂ term (w",0),("c",1),(" = −0.2, w = 0.2), the direction reported by Tong et al. (2024), gave −52.3 t CO₂e ha⁻¹ with ebullition close to zero. Alkalinity export (7.3 t CO₂ ha⁻¹) and carbonate accumulation (15 t CO₂ ha⁻¹) were identical across the four structures (Fig. 7).",0)]
p1=f'<w:p>{pp(ppr)}<w:ins w:id="{I()}" {D}>'+''.join(f'<w:r>{RS if sb else R}<w:t xml:space="preserve">{t}</w:t></w:r>' for t,sb in segs)+'</w:ins></w:p>'
interp=("These results constrain how a silicon effect on rice roots could lower CH₄ emission. Plant transport carries CH₄ through the rhizosphere, where much of it is oxidised; restricting its entry into roots leaves CH₄ to accumulate in porewater and escape largely unoxidised as bubbles. A plant-mediated Si effect that lowers emission must therefore act by supplying O₂ to the root zone, which in the model mainly suppresses anaerobic decomposition and methanogenesis, rather than by reducing gas exchange across the root barrier. The response is asymmetric: the simulated net GHG benefit is robust to Si making the barrier leakier (−52.3 vs −50.0 t CO₂e ha⁻¹) but is largely lost if Si tightens it. The size of the redirection depends on the ebullition parameterisation, which releases CH₄ at a first-order rate once porewater pCH₄ exceeds 0.4 atm. Separating plant-mediated, ebullitive and diffusive fluxes in amended and control plots would discriminate between these structures (Sect. 5.3).")
p2=f'<w:p>{pp(ppr)}<w:ins w:id="{I()}" {D}><w:r>{RH}<w:t xml:space="preserve">{interp}</w:t></w:r></w:ins></w:p>'
s=s[:pe]+p1+p2+s[pe:]
# 4. new Fig. 7 caption after the Fig. 6 caption
caps=[x for x in re.finditer(r'<w:p [^>]*>(?:(?!</w:p>).)*</w:p>',s) if re.sub(r'<[^>]+>','',x.group(0)).startswith('Fig. 6.')]
c6=caps[-1]; cppr=(re.search(r'<w:pPr>.*?</w:pPr>',c6.group(0)) or None); cppr=cppr.group(0) if cppr else '<w:pPr></w:pPr>'
RC=rpr_of(re.search(RUN,c6.group(0)).group(0))
cap=('Fig. 7. [PLACEHOLDER: figure file paddy/v24/cdr24.png] Alternative structures for the Si–root response at the reference site, 20 t basalt ha⁻¹ yr⁻¹ over ten years: Si raises root O₂ release (w = 0.2, as in the main runs); Si lowers plant CH₄ conductance (w_c = 0.5); Si lowers both plant CH₄ conductance and root O₂ release (w_c = w_r = 0.5); and a leakier barrier combined with the O₂ term (w_c = −0.2, w = 0.2). Panels show cumulative net realised GHG change and its CH₄, N₂O, alkalinity and carbonate components relative to matched controls, and annual CH₄ emission by pathway (plant-mediated, ebullition, diffusion).')
s=s[:c6.end()]+f'<w:p>{pp(cppr)}<w:ins w:id="{I()}" {D}><w:r>{RC}<w:t xml:space="preserve">{cap}</w:t></w:r></w:ins></w:p>'+s[c6.end():]
# 5. GWP* citation -> Allen et al. (2018) and Cain et al. (2019)
runs=list(re.finditer(RUN,s))
k=[i for i,x in enumerate(runs) if re.search(r'<w:t[^>]*>Planavsky</w:t>',x.group(0)) and 'formulation of' in s[x.start()-3000:x.start()]][0]
r1=runs[k]; nxt=[x for x in runs[k+1:k+5] if ' et al. (2026), E_CO' in x.group(0)][0]
rp=rpr_of(r1.group(0)); t2=re.search(r'<w:t[^>]*>(.*)</w:t>',nxt.group(0)).group(1); rp2=rpr_of(nxt.group(0))
rest=t2.split(' et al. (2026)',1)[1]
rep2=(f'<w:r>{rp2}<w:t xml:space="preserve"> et al. (</w:t></w:r><w:del w:id="{I()}" {D}><w:r>{rp2}<w:delText>2026</w:delText></w:r></w:del>'
      f'<w:ins w:id="{I()}" {D}><w:r>{rp2}<w:t>2019</w:t></w:r></w:ins><w:r>{rp2}<w:t xml:space="preserve">){rest}</w:t></w:r>')
rep1=(f'<w:del w:id="{I()}" {D}><w:r>{rp}<w:delText>Planavsky</w:delText></w:r></w:del><w:ins w:id="{I()}" {D}><w:r>{rp}<w:t>Allen et al. (2018) and Cain</w:t></w:r></w:ins>')
s=s[:nxt.start()]+rep2+s[nxt.end():]
s=s[:r1.start()]+rep1+s[r1.end():]
# delete the Planavsky et al. (2026) reference and add Cain et al. (2019)
j=s.find('Planavsky, N. J., Woollen'); a=s.rfind('<w:p ',0,j); b=s.find('</w:p>',j)+6
para=s[a:b]; ppx=re.search(r'<w:pPr>.*?</w:pPr>',para).group(0)
n=I(); ppy=ppx.replace('<w:rPr>',f'<w:rPr><w:del w:id="{n}" {D}/>',1) if '<w:rPr>' in ppx else ppx.replace('</w:pPr>',f'<w:rPr><w:del w:id="{n}" {D}/></w:rPr></w:pPr>')
body=para.split('</w:pPr>',1)[1]
body=re.sub(RUN,lambda m:f'<w:del w:id="{I()}" {D}>'+m.group(0).replace('<w:t>','<w:delText>').replace('<w:t xml:space="preserve">','<w:delText xml:space="preserve">').replace('</w:t>','</w:delText>')+'</w:del>',body)
s=s[:a]+para.split(ppx,1)[0]+ppy+body+s[b:]
paras=[(x.start(),re.sub(r'<[^>]+>','',x.group(0))) for x in re.finditer(r'<w:p [^>]*>(?:(?!</w:p>).)*</w:p>',s)]
start=s.find('Allen, M. R., Shine')
tgt=[(q,t) for q,t in paras if q>start and re.match(r'^[A-Z][^,]{1,25}, [A-Z]\.',t) and t>'Cain, M.'][0]
RR='<w:rPr><w:sz w:val="22"/><w:szCs w:val="32"/></w:rPr>'
ref='Cain, M., Lynch, J., Allen, M. R., Fuglestvedt, J. S., Frame, D. J., and Macey, A. H.: Improved calculation of warming-equivalent emissions for short-lived climate pollutants, npj Clim. Atmos. Sci., 2, 29, https://doi.org/10.1038/s41612-019-0086-4, 2019.'
s=s[:tgt[0]]+f'<w:p><w:pPr><w:ind w:left="284" w:hanging="284"/><w:rPr><w:ins w:id="{I()}" {D}/></w:rPr></w:pPr><w:ins w:id="{I()}" {D}><w:r>{RR}<w:t>{ref}</w:t></w:r></w:ins></w:p>'+s[tgt[0]:]
print('Cain inserted before:',tgt[1][:30])
open(p,'w').write(s)
