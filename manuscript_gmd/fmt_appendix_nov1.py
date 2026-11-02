import re
d=open('x/word/document.xml',encoding='utf8').read()
s=d.find('Appendix A: Rate laws'); s=d.find('</w:p>',s)+6; e=d.find('>Code and data availability<'); e=max(d.rfind('<w:p ',0,e),d.rfind('<w:p>',0,e))
seg=d[s:e]
seg=re.sub(r'<w:rFonts w:asciiTheme="majorBidi"[^>]*/>','',seg)
seg=seg.replace('<w:highlight w:val="yellow"/>','')
seg=seg.replace('<w:sz w:val="24"/>','<w:sz w:val="22"/>').replace('<w:szCs w:val="24"/>','<w:szCs w:val="22"/>')
seg=re.sub(r'<w:tbl>.*?</w:tbl>',lambda m:m.group().replace('<w:p ','<w:P ').replace('<w:p>','<w:P>').replace('</w:p>','</w:P>'),seg,flags=re.S)
def fixp(m):
    p=m.group()
    txt=''.join(re.findall(r'<w:t[^>]*>([^<]*)',p))
    if 'Heading2' in p: return p
    if '<m:oMath' in p and not txt.strip(): return p
    # body paragraph: 11 pt, Normal with first-line indent (not table captions)
    p=re.sub(r'<w:pStyle w:val="(?:BodyText|FirstParagraph)"/>','' if txt.startswith('Table A') else '<w:ind w:firstLine="284"/>',p)
    def addsz(r):
        rr=r.group()
        if '<w:sz ' in rr: return rr
        if '<w:rPr>' in rr: return rr.replace('<w:rPr>','<w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/>',1).replace('<w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/>','<w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/>',1)
        return rr.replace('>','><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>',1)
    p=re.sub(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',addsz,p,flags=re.S)
    return p
seg=re.sub(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>',fixp,seg,flags=re.S)
seg=seg.replace('<w:P ','<w:p ').replace('<w:P>','<w:p>').replace('</w:P>','</w:p>')
d=d[:s]+seg+d[e:]
open('x/word/document.xml','w',encoding='utf8').write(d)
st=open('x/word/styles.xml',encoding='utf8').read()
st=st.replace('<w:pPr><w:spacing w:before="36" w:after="36"/></w:pPr>','<w:pPr><w:spacing w:before="36" w:after="36" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>')
open('x/word/styles.xml','w',encoding='utf8').write(st); print('ok')
