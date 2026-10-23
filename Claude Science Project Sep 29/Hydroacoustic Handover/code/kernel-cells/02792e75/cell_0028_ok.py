t=re.sub(r"\s+"," ",trs["tr006"][2])
for pat in [r"15[:.]?47",r"1547",r"3[:.]47",r"afternoon",r"36 hours"]:
    for m in re.finditer(pat,t): print(pat,"|",t[max(0,m.start()-200):m.end()+150]); 
print(trs["tr006"][1], trs["tr007"][1], trs["tr009"][1])
t9=re.sub(r"\s+"," ",trs["tr009"][2]); i=t9.find("discounted as a credible"); print(t9[i-900:i+100])