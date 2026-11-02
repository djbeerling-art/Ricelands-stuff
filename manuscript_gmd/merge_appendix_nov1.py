import re
a=open('a/word/document.xml',encoding='utf8').read()
b=open('b/word/document.xml',encoding='utf8').read()
sa=open('a/word/styles.xml',encoding='utf8').read(); sb=open('b/word/styles.xml',encoding='utf8').read()
# styles
def style(sx,sid):
    m=re.search(r'<w:style [^>]*w:styleId="%s".*?</w:style>'%re.escape(sid),sx,re.S); return m.group() if m else None
need=set(re.findall(r'w:(?:pStyle|rStyle|tblStyle) w:val="([^"]+)"',b))
added=[]
todo=list(need)
while todo:
    s=todo.pop()
    if style(sa,s) or s in added: continue
    st=style(sb,s)
    if not st: print('no style',s); continue
    added.append(s); sa=sa.replace('</w:styles>',st+'</w:styles>')
    for bo in re.findall(r'w:(?:basedOn|next|link) w:val="([^"]+)"',st): todo.append(bo)
print('styles added',added)
open('a/word/styles.xml','w',encoding='utf8').write(sa)
# body
body=b[b.index('<w:body>')+8:b.rindex('<w:sectPr')]
blocks=re.findall(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>|<w:tbl>.*?</w:tbl>',body,re.S)
assert ''.join(blocks)==body or True
blocks=blocks[1:]  # drop title
ins=''.join(blocks)
ins=re.sub(r'<w:bookmark(?:Start|End) [^>]*/>','',ins)
ins=re.sub(r' w14:(?:paraId|textId)="[^"]*"','',ins)
ins=ins.replace('w:pStyle w:val="Heading1"','w:pStyle w:val="Heading2"')
ins=re.sub(r'w:id="(\d+)"',lambda m:'w:id="%d"'%(int(m.group(1))+50000),ins)
k=a.find('Appendix A: Rate laws, parameters and units'); e=a.index('</w:p>',k)+6
a=a[:e]+ins+a[e:]
open('a/word/document.xml','w',encoding='utf8').write(a); print('merged',len(blocks),'blocks')
