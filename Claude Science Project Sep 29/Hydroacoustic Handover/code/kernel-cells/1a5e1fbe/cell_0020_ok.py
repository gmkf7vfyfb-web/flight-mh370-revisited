def pgp(pos):
    f=re.findall(r'›\s*(\d+)\s*‹',a[:pos]); return f[-1] if f else None
seen=set()
for kw in ['weather','sea state','suspended','cyclone','visibility']:
    for m in re.finditer(kw,a,re.I):
        p=pgp(m.start())
        if p is None or int(p)>40: continue
        s=re.sub(r'\s+',' ',a[max(0,m.start()-220):m.end()+220])
        key=(p,s[:60])
        if key in seen: continue
        seen.add(key); print(f'p{p} [{kw}]',s); print()
# zero-area rows
for m in re.finditer(r'(\d{1,2}-(?:Mar|Apr)-14)\s+([^\n]{0,120})',a):
    row=m.group(2)
    if re.search(r'\b0 N/A|N/A|suspend|weather',row,re.I): print(m.group(1),row, 'p',pgp(m.start()))