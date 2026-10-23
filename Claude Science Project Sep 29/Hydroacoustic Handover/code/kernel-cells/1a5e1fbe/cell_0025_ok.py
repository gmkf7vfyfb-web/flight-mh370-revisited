blocks=re.split(r'\n##### ',j)
for b in blocks:
    name=b.split('\n')[0]
    if any(k in name for k in ['mr030','mr031','mr032','mr033','mr034','mr035','mr036','mr038','mr039','mr040','mr041','mr042']):
        d=re.search(r'Media Release\s*\n\s*([^\n]+)',b); 
        print(name, '|', d.group(1) if d else '?', '|', re.sub(r'\s+',' ',b[b.find('Media Release'):][:330]))