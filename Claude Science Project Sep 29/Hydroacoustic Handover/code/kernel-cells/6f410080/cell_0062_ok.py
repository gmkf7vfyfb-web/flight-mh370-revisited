for f,t in docs.items():
    if f.startswith('jacc/'):
        for m in re.finditer(r'[^.]{0,300}satellite[^.]{0,300}\.',t,re.I):
            s=m.group(0)
            if re.search(r'imag|object|debris|photo',s,re.I): print(f[5:],'|',s.strip()[:500])