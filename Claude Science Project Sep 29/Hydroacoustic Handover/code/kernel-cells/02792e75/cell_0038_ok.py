def page_text(n):
    s=[x for x in pages if x[1]==n]; e=[x for x in pages if x[1]==n+1]
    return t[s[0][0]:e[0][0]] if s and e else ""
seg=[]
for n in [23,24,116,117,118,119]:
    pt=page_text(n); 
    # compress table junk
    pt=re.sub(r"\n\*\*.{1,6}\*\*\n","",pt); pt=re.sub(r"\n{2,}","\n",pt)
    seg.append(f"#### printed p.{n}\n{pt}")
open("ctx_img.txt","w").write("\n".join(seg)); print(sum(len(x) for x in seg))