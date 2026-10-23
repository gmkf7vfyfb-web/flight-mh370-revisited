k=txt.find('Figure 6. Selected particles'); print(txt[k:k+5000])
for kw in ['Update','Griffin','ATSB','RNZAF']:
    for m in list(re.finditer(kw,txt))[:6]:
        pass
u=txt.find('Update on'); print('UPD',u, txt[u:u+3000] if u>=0 else '')