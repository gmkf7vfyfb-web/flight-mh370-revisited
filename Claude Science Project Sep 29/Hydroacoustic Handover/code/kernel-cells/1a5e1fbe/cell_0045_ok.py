r=host.artifacts(search='atsb_first_principles_review_dec2016')
v=r['artifacts'][0]; print(v['filename'],v['latest_version_id'])
F=pymupdf.open(host.artifact_path(v['latest_version_id']))
for i,p in enumerate(F):
    t=re.sub(r'\s+',' ',p.get_text())
    for m in re.finditer(r'[^.]*(surface search|aerial|probability of detection)[^.]*\.',t,re.I):
        print('PDF p',i+1,'||',m.group(0).strip()[:450])