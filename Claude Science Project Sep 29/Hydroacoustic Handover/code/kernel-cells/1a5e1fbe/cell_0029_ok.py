print(re.sub(r'\s+',' ',mt[20])[:900])
st=pages('stone2014.pdf'); print(len(st))
for i,t in enumerate(st):
    tt=re.sub(r'\s+',' ',t)
    for m in re.finditer(r'[^.]*(surface search|life raft|four-person|aerial search|30%|0\.3)[^.]*\.',tt,re.I):
        print('Stone PDF p',i+1,'||',m.group(0).strip()[:400])