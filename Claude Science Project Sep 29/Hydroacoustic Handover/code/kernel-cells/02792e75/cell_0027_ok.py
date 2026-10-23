txt=[]
for k in ["tr006","tr007","tr008","tr009","tr010"]:
    t=re.sub(r"\s+"," ",trs[k][2]); pos=[m.start() for m in re.finditer(r"Haixun|[Ww]hite obj|white|Echo|submarine|90 kilo|two kilo|2 kilo",t)]
    spans=[]
    for p in pos:
        a,b=max(0,p-250),p+350
        if spans and a<=spans[-1][1]: spans[-1][1]=b
        else: spans.append([a,b])
    txt.append(f"##### {k}\n"+"\n...\n".join(t[a:b] for a,b in spans))
open("ctx_tr.txt","w").write("\n".join(txt)); print(sum(len(x) for x in txt))