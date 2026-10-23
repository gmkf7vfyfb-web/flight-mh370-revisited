s4=strokes(3)
L4=[l for l in s4 if l[0]!='re' and (abs(l[0]-l[2])>50 or abs(l[1]-l[3])>30)]
print(sorted(set(L4)))
sh4=[l for l in s4 if l[0]!='re' and l not in L4]
xt=sorted(set(l[0] for l in sh4 if l[0]==l[2])); yt=sorted(set(l[1] for l in sh4 if l[1]==l[3]))
print("xticks",xt); print("yticks",yt)
host.view_image(r2[2]['image_path'], crop=(800,250,1400,1300))