
keep=[]
for i in [1,2,3,5,13,14,15,16,17,18,19,20]:
    for ln in bl[i-1].split("\n"):
        if re.search(r"(ditch|glide|L/D|touchdown|vertical speed|fpm|flare|drift ?down|Nm|kt\b|flap)",ln,re.I):
            keep.append(f"p{i}| "+ln.strip())
open("src/blelly_hits.txt","w").write("\n".join(keep))
print(len(keep))
