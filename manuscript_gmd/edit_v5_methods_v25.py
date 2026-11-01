# Tracked edits: v25 methods (ferrihydrite ageing, goethite rate, floodwater solute discharge) on Nov1_v5
import re,sys,html,os,shutil,subprocess,tempfile
src,dst=sys.argv[1],sys.argv[2]
tmp=tempfile.mkdtemp(); subprocess.run(['unzip','-q',src,'-d',tmp],check=True)
P=os.path.join(tmp,'word/document.xml'); d=open(P,encoding='utf8').read()
DATE='2026-11-01T09:10:00Z'; AU='Claude'
ids=[int(x) for x in re.findall(r'w:id="(\d+)"',d)]; nid=[max(ids+[0])+5000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
def esc(s): return html.escape(s,quote=False)
def edit(ctx,old,new,hl=False,AT=None):
    global d
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if ectx in m.group()]
    assert len(hits)==1,(ctx,len(hits))
    m=hits[0]; r=m.group(); assert r.count('<w:t')==1,ctx
    head=re.match(r'<w:r(?: [^>]*)?>',r).group()
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',r,re.S); rpr=rpr.group() if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',r,re.S); pre=r[len(head):tm.start()]
    text=tm.group(1)
    i=text.index(ectx)+ectx.index(esc(old)) if old else text.index(ectx)+(len(ectx) if AT is None else AT)
    before,after=text[:i],text[i+len(esc(old)):]
    T=lambda s:'<w:t xml:space="preserve">%s</w:t>'%s
    out=head+pre+T(before)+'</w:r>'
    if old: out+='<w:del w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'%(wid(),AU,DATE,rpr,esc(old))
    if new:
        rp2=rpr
        if hl: rp2=rpr.replace('</w:rPr>','<w:highlight w:val="cyan"/></w:rPr>') if rpr else '<w:rPr><w:highlight w:val="cyan"/></w:rPr>'
        out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins>'%(wid(),AU,DATE,rp2,T(esc(new)))
    if after: out+=head+rpr+T(after)+'</w:r>'
    d=d[:m.start()]+out+d[m.end():]
PARA=re.compile(r'<w:p(?: [^>]*)?>(?:(?!</w:p>).)*?</w:p>',re.S)
def newpara_before(anchor,text):
    global d
    hits=[m for m in PARA.finditer(d) if ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',m.group())).startswith(esc(anchor))]; assert len(hits)==1,(anchor,len(hits))
    p=hits[0].group()
    ppr=re.search(r'<w:pPr>.*?</w:pPr>',p,re.S); ppr=ppr.group() if ppr else '<w:pPr></w:pPr>'
    mark='<w:ins w:id="%d" w:author="%s" w:date="%s"/>'%(wid(),AU,DATE)
    if '<w:rPr>' in ppr: ppr=ppr.replace('<w:rPr>','<w:rPr>'+mark,1)
    else: ppr=ppr.replace('</w:pPr>','<w:rPr>'+mark+'</w:rPr></w:pPr>')
    rpr=re.search(r'<w:r(?: [^>]*)?>\s*(<w:rPr>.*?</w:rPr>)',p,re.S); rpr=rpr.group(1) if rpr else ''
    np='<w:p>'+ppr+'<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:ins></w:p>'%(wid(),AU,DATE,rpr,esc(text))
    d=d[:hits[0].start()]+np+d[hits[0].start():]

# 2.4 Fe
edit('reduced approximately 30 times','30','5')
edit('incorporated into secondary minerals.','',' Ferrihydrite ages to goethite at a first-order rate of 0.3 yr⁻¹, catalysed by dissolved Fe(II) and inhibited by dissolved Si (Hansel et al., 2005; Jones et al., 2009); the ageing rate and the goethite reduction rate were set so that the untreated reference column keeps a steady Fe(III) inventory and CH₄ baseline over multi-year runs (Appendix A).')
# 2.6.2 floodwater discharge
edit('(approximately 1.4 mm d','',' While the surface is flooded, solutes in the top cell also exchange with floodwater that is continually renewed at the irrigation-water composition and discharged laterally, representing over-bund outflow and drainage to ditches. The discharge is set to 200 mm of floodwater per season under all water regimes, with 100 and 400 mm as low and high cases; reported seasonal surface outflows from irrigated and rainfed paddies range from about 100 to 430 mm (Bouman et al., 2007; Sujono, 2010; Peng et al., 2012; Qi et al., 2020). Pot and batch experiments are closed at the surface.',AT=len('(approximately 1.4 mm d⁻¹).'))
edit('surface-water storage or irrigation runoff','irrigation runoff','storm-driven runoff')
edit('imposed management forcings.','',' Floodwater discharge is a constant prescribed rate while the surface is flooded.')
# Appendix A2 goethite + ageing
edit('Goethite and hematite are not allowed','',' Ferrihydrite ageing (fhage), Fe(OH)₃ → FeOOH + H₂O (−1 amfe3, +1 gt), has rate k amfe3 M([Fe(II)], 10⁻⁴ M) I([Si], 3 × 10⁻⁴ M) f_(sat), with k = 0.3 yr⁻¹; goethite therefore forms only by this reaction. ',AT=0)
edit('v = 10 ','10','60')
# A6 floodwater solutes
edit('(0.1 m d','',' While flooded, dissolved solutes in the top cell also exchange with floodwater renewed at the irrigation-water composition (Table A6). The exchange coefficient is the discharge rate k_(aq) w_(fw) in series with diffusion across the upper half of the top cell, and the resulting flux is the lateral export reported as floodwater discharge. k_(aq) = 0.74 m yr⁻¹ of flooded time under continuous flooding and 0.96 m yr⁻¹ under AWD and the rainfed schedule (200 mm per season; --kaq). Lateral alkalinity export is the charge-weighted sum of the discharged Ca, Mg, Na, K and Fe(II) minus SO₄, Cl and NO₃, and is added to the alkalinity exported through the base; PDA subtracts 2Fe(II) in both.',AT=len('(0.1 m d⁻¹).'))
edit('floodwater gas-exchange velocity','','; floodwater_aq.in: floodwater solute discharge rate (--kaq)')
edit('free outflow at the base','','; floodwater discharge 200 mm per season while flooded, renewed at the irrigation-water composition (--kaq); none in pots and batch experiments')
# Fig 1 caption
edit('goethite is reduced ~30','30','5')
edit('exported through the base (PDA','',' and in floodwater discharge',AT=len('exported through the base'))
# References
newpara_before('Bourrié, G., Trolard','Bouman, B. A. M., Lampayan, R. M., and Tuong, T. P.: Water Management in Irrigated Rice: Coping with Water Scarcity, International Rice Research Institute, Los Baños, Philippines, 2007.')
newpara_before('Hartmann, J. and Moosdorf','Hansel, C. M., Benner, S. G., and Fendorf, S.: Competing Fe(II)-induced mineralization pathways of ferrihydrite, Environ. Sci. Technol., 39, 7147–7153, https://doi.org/10.1021/es050666z, 2005.')
newpara_before('Jordan, J. S., Mills','Jones, A. M., Collins, R. N., Rose, J., and Waite, T. D.: The effect of silica and natural organic matter on the Fe(II)-catalysed transformation and reactivity of Fe(III) minerals, Geochim. Cosmochim. Acta, 73, 4409–4422, https://doi.org/10.1016/j.gca.2009.04.025, 2009.')
newpara_before('Poggio, L., de Sousa','Peng, S., Luo, Y., Xu, J., Khan, S., Jiao, X., and Wang, W.: Integrated irrigation and drainage practices to enhance water productivity and reduce pollution in a rice production system, Irrig. Drain., 61, 285–293, https://doi.org/10.1002/ird.684, 2012.')
newpara_before('Reershemius, T., Kelland','Qi, D., Wu, Q., and Zhu, J.: Nitrogen and phosphorus losses from paddy fields and the yield of rice with different water and nitrogen management practices, Sci. Rep., 10, [article number to check], https://doi.org/10.1038/s41598-020-66757-5, 2020.')
newpara_before('Tong, S., Ranathunge','Sujono, J.: Flood reduction function of paddy rice fields under different water saving irrigation techniques, J. Water Resour. Prot., 2, 555–559, https://doi.org/10.4236/jwarp.2010.26063, 2010.')
open(P,'w',encoding='utf8').write(d)
out=os.path.abspath(dst)
subprocess.run('cd %s && zip -q -r -X %s .'%(tmp,out),shell=True,check=True)
print('ok')
