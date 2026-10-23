mt=pages('metron.pdf'); print(len(mt))
for i,t in enumerate(mt):
    if re.search(r'Surface Search|life ?raft|sweep width|POD|probability of detection',t,re.I) and i<30:
        print('== PDF p',i+1); print(re.sub(r'\s+',' ',t)[:3500])