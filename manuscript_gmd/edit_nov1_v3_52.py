import re,sys,html
src,dst=sys.argv[1],sys.argv[2]
d=open(src,encoding='utf8').read()
DATE='2026-11-01T09:00:00Z'; AU='Claude'
ids=[int(x) for x in re.findall(r'w:id="(\d+)"',d)]; nid=[max(ids+[0])+1000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
def esc(s): return html.escape(s,quote=False)
def edit(ctx,old,new,hl=False,AT=None):
    global d
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if ectx in m.group()]
    assert len(hits)==1,(ctx,len(hits))
    m=hits[0]; r=m.group()
    assert r.count('<w:t')==1,ctx
    head=re.match(r'<w:r(?: [^>]*)?>',r).group()
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',r,re.S); rpr=rpr.group() if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',r,re.S)
    pre=r[len(head):tm.start()]  # rPr + e.g. lastRenderedPageBreak
    text=tm.group(1); i=text.index(ectx)+ectx.index(esc(old)) if old else text.index(ectx)+len(ectx)
    if old=='' and AT is not None: i=text.index(ectx)+AT
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
# (a)(b)
edit('under flooded conditions','flooded','stagnant, flooding-like')
edit('which also governs the entry','also governs','may also restrict')
# (c) end of para 1 (insert cyan first so the factual one lands before it)
edit('rather than testing whether that structure is correct.',''," In these runs, CH₄ excluded from the plant pathway escaped mainly by ebullition and was therefore largely unoxidised, so the sign of the plant response to Si, not only its strength, needs to be established experimentally.",hl=True)
edit('rather than testing whether that structure is correct.','',' In an alternative structure in which dissolved Si lowers root CH₄ conductance instead of raising root O₂ release, ten-year net mitigation at 20 t basalt ha⁻¹ yr⁻¹ fell from approximately 50 to 3 t CO₂e ha⁻¹, and became a net increase of approximately 30 t CO₂e ha⁻¹ when Si also lowered root O₂ release; mitigation was retained (approximately 52 t CO₂e ha⁻¹) when Si made the barrier leakier (Sect. 4.2; Fig. 7).')
# (d)
edit('competition with methanogens (Ali et al., 2008; Das et al., 2022), and','Ali et al., 2008; ','')
edit('Das et al., 2022), and Si applied',''," CH₄ production also fell in root-free incubations of slag-amended soil (Ali et al., 2008),",AT=len('Das et al., 2022),'))
edit('Limmer et al., 2018), so part','','; reviewed by Das et al., 2022',AT=len('Limmer et al., 2018'))
edit('(Sect. 3.3). Mn cycling',''," With w = 0, the model lowers first-year CH₄ emission at the reference site by only about 2% (Fig. 6b) and raises first-year CH₄ production by about 12% (not shown).",AT=len('(Sect. 3.3).'))
edit(' Mn cycling, microbial',''," In the model, basalt-derived reduced-Fe phases consume root-zone O₂ and so weaken O₂ inhibition of anaerobic decomposition, which offsets the effect of Fe-reducer competition; whether this occurs in the field is untested.",hl=True,AT=0)
# (e)
edit('Fe ageing is another','ageing','redistribution')
edit('slower Fe ageing nor','ageing','redistribution')
open(dst,'w',encoding='utf8').write(d)
print('ok')
