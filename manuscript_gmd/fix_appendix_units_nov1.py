import re,html
src='a/word/document.xml'
d=open(src,encoding='utf8').read()
# split J equation onto two lines
d,n=re.subn(r'<m:r>(?:(?!</m:r>).)*? </m:t></m:r>','</m:oMath><m:oMath>',d,flags=re.S); assert n==1
DATE='2026-11-01T10:30:00Z'; AU='Claude'
nid=[max(int(x) for x in re.findall(r'w:id="(\d+)"',d))+1000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
def esc(s): return html.escape(s,quote=False)
T=lambda s:'<w:t xml:space="preserve">%s</w:t>'%s
def rtext(r): return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',r))
def edit_run(m,old,new,i):
    global d
    rr=m.group(); head=re.match(r'<w:r(?: [^>]*)?>',rr).group()
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',rr,re.S); rpr=rpr.group() if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',rr,re.S); pre=rr[len(head):tm.start()]; tx=tm.group(1)
    before,after=tx[:i],tx[i+len(esc(old)):]
    out=head+pre+T(before)+'</w:r>'
    if old: out+='<w:del w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'%(wid(),AU,DATE,rpr,esc(old))
    if new: out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins>'%(wid(),AU,DATE,rpr,T(esc(new)))
    if after: out+=head+rpr+T(after)+'</w:r>'
    d=d[:m.start()]+out+d[m.end():]
def edit(ctx,old,new,AT=None):
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if ectx in m.group()]
    assert len(hits)==1,(ctx,len(hits))
    tx=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',hits[0].group(),re.S).group(1)
    i=tx.index(ectx)+(AT if AT is not None else (ectx.index(esc(old)) if old else len(ectx)))
    edit_run(hits[0],old,new,i)
# 1 vmax units: all runs whose text starts 'v = <num> yr⁻¹' or Table A8 '1860 yr⁻¹', '300 yr⁻¹, 5.5'
cnt=0
while True:
    hits=[m for m in RUN.finditer(d) if '<w:delText' not in m.group() and re.match(r'(v = \d+ yr⁻¹|1860 yr⁻¹$|300 yr⁻¹, 5\.5)',rtext(m.group()))]
    if not hits: break
    m=hits[0]; tx=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',m.group(),re.S).group(1)
    i=tx.index('yr⁻¹'); edit_run(m,'','mol m⁻³ ',i); cnt+=1
print('vmax unit edits',cnt)
# 2 fsat: insert after the gpH/fO2 subscript runs in three rate-law cells
PAR=re.compile(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>',re.S)
def add_fsat(par_start,after_sub):
    global d
    hits=[m for m in PAR.finditer(d) if re.sub(r'<[^>]+>','',m.group()).startswith(par_start)]
    assert len(hits)==1,(par_start,len(hits))
    p=hits[0].group(); rs=list(RUN.finditer(p))
    k=[j for j,r in enumerate(rs) if rtext(r.group())==after_sub][-1]
    sub=rs[k].group(); f=rs[k-1].group()
    rp_sub=re.search(r'<w:rPr>.*?</w:rPr>',sub,re.S).group(); rp_f=re.search(r'<w:rPr>.*?</w:rPr>',f,re.S).group()
    ins='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r><w:r>%s%s</w:r><w:r>%s%s</w:r></w:ins>'%(wid(),AU,DATE,re.sub(r'<w:vertAlign[^>]*/>|<w:i/>','',rp_f),T(' '),rp_f,T('f'),rp_sub,T('sat'))
    pos=hits[0].start()+rs[k].end()
    d=d[:pos]+ins+d[pos:]
add_fsat('r v M(g2) M([NO','pH')
add_fsat('v M([NH','pH')
add_fsat('v M(g2) M([N2O]','O2')
# 3 siderite
edit('). Siderite is allowed to form at equilibrium.','Siderite is allowed to form at equilibrium.','Siderite may precipitate kinetically, but without a nucleation seed it forms only in trace amounts in the production runs.')
# 4 Si rationale + targets
edit('observations of Si-enhanced root oxidising capacity (Fleck et al., 2011), but its strength ','Fleck et al., 2011), but','Ma and Takahashi, 2002; Das et al., 2022), although Si has also been reported to strengthen (Fleck et al., 2011) or weaken (Tong et al., 2024) the root barrier to radial O₂ loss, and')
edit(' was fitted to a single field CH','a single field','the')
edit(' response (Gong et al., 2026). Because','response (Gong et al., 2026)','responses of a basalt pot experiment and a steel-slag field trial (Gong et al., 2026; Wang et al., 2014)')
edit('fitted to the Gong et al.\xa0(2026) CH','','',AT=None) if False else None
edit('fitted to the Gong et al.\xa0(2026) CH','Gong et al.\xa0(2026) CH','Gong et al.\xa0(2026) and Wang et al. (2014) CH')
edit(' response; sensitivity ','response','responses')
open(src,'w',encoding='utf8').write(d); print('ok')
