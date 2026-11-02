import re,sys,html
src,dst=sys.argv[1],sys.argv[2]
d=open(src,encoding='utf8').read()
MINUS='−'
def r(t,p=False): return '<m:r>%s<m:t xml:space="preserve">%s</m:t></m:r>'%('<m:rPr><m:sty m:val="p"/></m:rPr>' if p else '',html.escape(t,quote=False))
def sub(b,s): return '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>'%(b,s)
def sup(b,s): return '<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>'%(b,s)
def frac(n,dn): return '<m:f><m:num>%s</m:num><m:den>%s</m:den></m:f>'%(n,dn)
def dl(e,b='(',c=')'): return '<m:d><m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/></m:dPr><m:e>%s</m:e></m:d>'%(b,c,e)
def func(name,arg): return '<m:func><m:fName>%s</m:fName><m:e>%s</m:e></m:func>'%(r(name,True),arg)
def para(body): return '<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr><m:oMath>%s</m:oMath></m:oMathPara>'%body
eq={}
# N2O yield
eq['r']=para(r('r')+r('=',True)+r('0.1')+r('+',True)+frac(r('0.9'),r('1')+r('+',True)+sup(r('10'),r('pH',True)+r(MINUS,True)+r('6.2'))))
# Q10
eq['q10']=para(r('k')+dl(r('T'))+r('=',True)+sub(r('k'),r('25'))+r(' ')+sup(sub(r('Q'),r('10')),frac(r('T')+r(MINUS,True)+r('25'),r('10')))+r(',',True))
# floodwater
X=sub(dl(r('X'),'[',']'),r('top',True))
eq['J']=para(r('J')+r('=',True)+sub(r('k'),r('fw',True))+r(' ')+sub(r('w'),r('fw',True))+r(' ')+r('1000')+r(' ')
   +dl(X+r(MINUS,True)+sub(r('K'),r('H',True))+r(' ')+sub(r('p'),r('atm',True)))+r(',',True)+r(' ',True)
   +sub(r('w'),r('fw',True))+r('=',True)+func('min',dl(r('1')+r(',',True)+func('max',dl(r('0')+r(',',True)+frac(sub(r('S'),r('w,top',True))+r(MINUS,True)+r('0.9'),r('0.1')),'[',']')),'{','}'))+r(',',True))
ps=list(re.finditer(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>',d,re.S))
def text(p): return ''.join(re.findall(r'<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>',p))
rep=[]
for m in ps:
    p=m.group(); t=text(p)
    if '<m:oMathPara' not in p: continue
    k='r' if t.startswith('r=') else 'q10' if t.startswith('kT') else 'J' if t.startswith('J=') else None
    if k:
        newp=re.sub(r'<m:oMathPara>.*</m:oMathPara>',lambda _:eq[k],p,flags=re.S); rep.append((m.start(),m.end(),newp))
assert len(rep)==3,len(rep)
for s,e,n in reversed(rep): d=d[:s]+n+d[e:]
# tracked text edits
DATE='2026-11-01T09:30:00Z'; AU='Claude'
nid=[max(int(x) for x in re.findall(r'w:id="(\d+)"',d))+1000]
def wid():
    nid[0]+=1; return nid[0]
RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
def esc(s): return html.escape(s,quote=False)
def edit(ctx,old,new,AT=None):
    global d
    ectx=esc(ctx); hits=[m for m in RUN.finditer(d) if ectx in m.group()]
    assert len(hits)==1,(ctx,len(hits))
    m=hits[0]; rr=m.group(); assert rr.count('<w:t')==1,ctx
    head=re.match(r'<w:r(?: [^>]*)?>',rr).group()
    rpr=re.search(r'<w:rPr>.*?</w:rPr>',rr,re.S); rpr=rpr.group() if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>(.*?)</w:t>',rr,re.S); pre=rr[len(head):tm.start()]
    tx=tm.group(1)
    i=tx.index(ectx)+(AT if AT is not None else (ectx.index(esc(old)) if old else len(ectx)))
    before,after=tx[:i],tx[i+len(esc(old)):]
    T=lambda s:'<w:t xml:space="preserve">%s</w:t>'%s
    out=head+pre+T(before)+'</w:r>'
    if old: out+='<w:del w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'%(wid(),AU,DATE,rpr,esc(old))
    if new: out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins>'%(wid(),AU,DATE,rpr,T(esc(new)))
    if after: out+=head+rpr+T(after)+'</w:r>'
    d=d[:m.start()]+out+d[m.end():]
EDITS=[
 ('for the verification in Fig. 3. The two differ','',', and v24 (commit f2d2aa8) for the alternative Si–root structures in Fig. 7',dict(AT=len('for the verification in Fig. 3'))),
 ('The two differ only','The two','v22 and v23',{}),
 ('produced Figs. 4–8.','4–8','4–6, 8 and 9',{}),
 ('(irr061, year 1). The archived','',' v24 (commit f2d2aa8) adds the alternative Si–root-barrier structure (--ch4si; Sect. A5), which is used only for Fig. 7 and is off in all other runs.',dict(AT=len('(irr061, year 1).'))),
 ('loss does not depend on Si.','',' Fig. 7 alone uses an alternative empirical structure (--ch4si=KSi:[Si]ref:wc:wr, file ch4si.in) in which Si sets a root-barrier resistance b = 1 − w + w h([Si])/h([Si]ref): plant CH4 transport (ch4pl, ch4rx) is multiplied by 1/b(wc) and root O2 loss (rtoxy) by 1/b(wr), with KSi and [Si]ref as above.',{}),
  ('both exact versions (source at commits 162913a and 267a856','both','all three',{}),
  ('exact versions (source at commits 162913a and 267a856','162913a and 267a856','162913a, 267a856 and f2d2aa8',{}),
]
for a,b,c,kw in EDITS: edit(a,b,c,**kw)
open(dst,'w',encoding='utf8').write(d); print('ok')
