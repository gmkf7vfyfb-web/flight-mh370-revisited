def pg(pos):
    f=re.findall(r'›\s*(\d+)\s*‹',a[:pos]); return int(f[-1])+1 if f else None  # marker at page bottom? check
i=a.find('Surface search coverage and confidence**')
print(re.sub(r'\s+',' ',a[i-300:i+2600]))