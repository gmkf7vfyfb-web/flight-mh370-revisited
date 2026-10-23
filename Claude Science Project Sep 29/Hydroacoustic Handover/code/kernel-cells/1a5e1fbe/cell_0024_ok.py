j=open(host.artifact_path('3c19feec-1958-4efe-b488-5c92e5bdb538')).read()
print(j[:600])
for m in re.finditer(r'[^\n.]*(suspend|weather|cyclone|visibility|sea state|swell|rain|low cloud)[^\n.]*\.',j,re.I):
    pre=j[:m.start()]
    hdr=re.findall(r'(?m)^(=+.*|#+.*|mr\d+.*|.*mr0\d\d.*)$',pre)
    print((hdr[-1][:70] if hdr else '?'),'||',m.group(0).strip()[:260])