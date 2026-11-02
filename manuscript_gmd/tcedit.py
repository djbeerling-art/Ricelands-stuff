# Paragraph-level tracked-change helpers for Word docx (no existing tracked changes required).
# rep(old,new): tracked delete of 'old' (may span runs within one paragraph) and tracked insert of 'new' after it.
# ins_after(ctx,new): tracked insert after the unique text ctx. newpara_before(ctx,text): tracked new paragraph
# before the paragraph containing ctx (copies that paragraph's pPr, or pPr of the paragraph containing like).
import re,html,os,subprocess,tempfile
class Doc:
    RUN=re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',re.S)
    PARA=re.compile(r'<w:p(?: [^>]*)?>(?:(?!<w:p[ >]).)*?</w:p>',re.S)
    def __init__(s,src,date,author='Claude'):
        s.tmp=tempfile.mkdtemp(); subprocess.run(['unzip','-q',src,'-d',s.tmp],check=True)
        s.P=os.path.join(s.tmp,'word/document.xml'); s.d=open(s.P,encoding='utf8').read()
        s.DATE,s.AU=date,author
        s.nid=max([int(x) for x in re.findall(r'w:id="(\d+)"',s.d)]+[0])+7000
    def wid(s): s.nid+=1; return s.nid
    @staticmethod
    def TT(r): return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',r)))
    def ptext(s,p): return ''.join(s.TT(m.group()) for m in s.RUN.finditer(p) if '<w:delText' not in m.group())
    def find(s,old,n=None):
        hits=[]
        for pm in s.PARA.finditer(s.d):
            t=s.ptext(pm.group()); i=t.find(old)
            while i>=0: hits.append((pm,i)); i=t.find(old,i+1)
        if n is None: assert len(hits)==1,('not unique/absent',old[:80],len(hits))
        return hits[n or 0]
    def _rpr(s,r):
        m=re.search(r'<w:rPr>.*?</w:rPr>',r,re.S); return m.group() if m else ''
    def _t(s,x): return '<w:t xml:space="preserve">%s</w:t>'%html.escape(x,quote=False)
    def _hl(s,rpr,hl):
        if not hl: return rpr
        rpr=re.sub(r'<w:highlight [^>]*/>','',rpr)
        return rpr.replace('</w:rPr>','<w:highlight w:val="%s"/></w:rPr>'%hl) if rpr else '<w:rPr><w:highlight w:val="%s"/></w:rPr>'%hl
    def span(s,start,old,new,hl=None,n=None):
        pm,i=s.find(start+old,n) if True else None
        i+=len(start); e=i+len(old); p=pm.group(); out=''; pos=0; last=0; done=False; rpr0=None
        runs=list(s.RUN.finditer(p))
        for m in runs:
            r=m.group(); t=s.TT(r); a,b=pos,pos+len(t); pos=b
            out+=p[last:m.start()]; last=m.end()
            hit=(a<e and b>i) if old else False
            ipt=(not done) and (a<e<=b if old else a<i<=b or (i==0 and a==0 and b>0))
            if not hit and not ipt: out+=r; continue
            assert r.count('<w:t')==1 and '<w:delText' not in r,('complex run',t)
            head=re.match(r'<w:r(?: [^>]*)?>',r).group(); rpr=s._rpr(r)
            if rpr0 is None: rpr0=rpr
            k1,k2=max(a,i)-a,min(b,e)-a
            if not old: k1=k2=i-a
            if k1>0: out+=head+rpr+s._t(t[:k1])+'</w:r>'
            if k2>k1: out+='<w:del w:id="%d" w:author="%s" w:date="%s"><w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'%(s.wid(),s.AU,s.DATE,rpr,html.escape(t[k1:k2],quote=False))
            if ipt and new:
                out+='<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins>'%(s.wid(),s.AU,s.DATE,s._hl(rpr0,hl),s._t(new)); done=True
            elif ipt: done=True
            if k2<len(t): out+=head+rpr+s._t(t[k2:])+'</w:r>'
        out+=p[last:]
        assert done or not new,('insert point not found',old[:60])
        s.d=s.d[:pm.start()]+out+s.d[pm.end():]
    def rep(s,old,new,hl=None,n=None,pre=''): s.span(pre,old,new,hl,n)
    def ins_after(s,ctx,new,hl=None,n=None): s.span(ctx,'',new,hl,n)
    def flag(s,ctx,text,n=None): s.ins_after(ctx,' ['+text+']','yellow',n)
    def newpara_before(s,ctx,text,hl=None,like=None):
        pm,_=s.find(ctx); lp=s.find(like)[0].group() if like else pm.group()
        ppr=re.search(r'<w:pPr>.*?</w:pPr>',lp,re.S); ppr=ppr.group() if ppr else '<w:pPr></w:pPr>'
        mark='<w:ins w:id="%d" w:author="%s" w:date="%s"/>'%(s.wid(),s.AU,s.DATE)
        ppr=ppr.replace('</w:pPr>','<w:rPr>%s</w:rPr></w:pPr>'%mark) if '<w:rPr>' not in ppr else re.sub(r'<w:rPr>','<w:rPr>'+mark,ppr,1)
        r0=[m.group() for m in s.RUN.finditer(lp) if s.TT(m.group())]
        rpr=s._hl(s._rpr(r0[0]) if r0 else '',hl)
        rpr=re.sub(r'<w:(b|i)(?: [^>]*)?/>','',rpr)
        np='<w:p>%s<w:ins w:id="%d" w:author="%s" w:date="%s"><w:r>%s%s</w:r></w:ins></w:p>'%(ppr,s.wid(),s.AU,s.DATE,rpr,s._t(text))
        s.d=s.d[:pm.start()]+np+s.d[pm.start():]
    def save(s,dst):
        open(s.P,'w',encoding='utf8').write(s.d); out=os.path.abspath(dst)
        if os.path.exists(out): os.remove(out)
        subprocess.run('cd %s && zip -q -r -X %s .'%(s.tmp,out),shell=True,check=True)
