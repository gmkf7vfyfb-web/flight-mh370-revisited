out=[]
for k in ["tr006","tr007","tr008","tr009","tr010"]:
    t=re.sub(r"\s+"," ",trs[k][2])
    for m in re.finditer(r"Haixun|white|objects|kilometres|Echo|submarine|Tireless|Chinese",t):
        out.append((k,m.start()))
# merge windows
txt=[]
for k in ["tr006","tr007","tr008","tr009","tr010"]:
    t=re.sub(r"\s+"," ",trs[k][2]); pos=sorted(p for kk,p in out if kk==k)
    spans=[]
    for p in pos:
        a,b=max(0,p-350),p+450
        if spans and a<=spans[-1][1]: spans[-1][1]=b
        else: spans.append([a,b])
    txt.append(f"##### {k} {trs[k][1]}\n"+"\n...\n".join(t[a:b] for a,b in spans))
open("ctx_tr.txt","w").write("\n".join(txt)); print(sum(len(x) for x in txt))