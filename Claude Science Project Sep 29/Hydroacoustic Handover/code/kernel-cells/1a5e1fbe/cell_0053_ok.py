def parse(pg):
    t=doc[pg].get_text()
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    out={}; cur=None; nums=[]
    for l in lines:
        toks=l.split()
        if all(re.fullmatch(r'\d+\.\d',x) for x in toks):
            if cur is not None: nums+= [float(x) for x in toks]
            if cur and len(nums)>=12: out[cur]=nums[:12]; cur=None; nums=[]
        else:
            cur=l; nums=[]
    return out
t1=parse(401); t2=parse(403)
keep1=['Person in water','Raft 1 person','Raft 4 Person','Raft 6 Person','Power Boat <5 m (15 ft)','Power Boat 5-8 m (15-25 ft)']
keep2=['Person in Water','Raft 1 person','Raft 4 person','Raft 6 person','Power Boat <5 (15 ft)','Power Boat 6 (20 ft)']
vis=['2','5','10','20','30','>40']
rows=[]
for k in keep1:
    v=t1[k]; rows.append([k,'500 ft (150 m)']+v[:6]); rows.append([k,'1000 ft (300 m)']+v[6:])
for k in keep2:
    v=t2[k]; rows.append([k,'1500 ft (450 m)']+v[:6]); rows.append([k,'2000 ft (600 m)']+v[6:])
swt=pd.DataFrame(rows,columns=['Object','Altitude']+[f'Vis {x} km' for x in vis])
print(swt.to_string())