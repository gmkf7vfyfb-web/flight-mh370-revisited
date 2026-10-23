res=[]
for Wu,lab in [(2.3,'4-person raft, 1000 ft, vis >40 km'),(1.3,'4-person raft, 1000 ft, vis 10 km'),(1.4,'1-person raft, 1000 ft, vis >40 km')]:
    for fw in [1.0,0.5,0.25]:
        for S in [4,12,16]:
            C=Wu*fw/S
            res.append([lab,fw,S,round(C,3),round(1-math.exp(-C),3),round(math.erf(math.sqrt(math.pi)/2*C),3)])
pt=pd.DataFrame(res,columns=['Case','Fw','S (NM)','C=W/S','POD exponential','POD inverse cube'])
print(pt.to_string())
print([round(1-math.exp(-c),3) for c in (0.5,1.0)],[round(math.erf(math.sqrt(math.pi)/2*c),3) for c in (0.5,1.0)])
# 5 repeated searches at C=0.5 inverse cube cum: NATSAR uses average C; check (1-(1-p)^5)
p=math.erf(math.sqrt(math.pi)/2*0.5); print(1-(1-p)**5, math.erf(math.sqrt(math.pi)/2*0.5*math.sqrt(5)))