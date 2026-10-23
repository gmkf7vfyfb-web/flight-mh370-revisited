s=2550/1224
ann={27:[(633,650),(827,844),(1016,1033)],28:[(457,475),(669,688),(1168,1186)],29:[(452,470),(675,693),(888,906)],
30:[(345,364),(563,582),(780,798),(1090,1109),(1320,1340)],31:[(620,640),(838,858),(1056,1075)],
32:[(344,363),(563,582),(780,798),(1075,1094),(1293,1312)],33:[(403,422),(621,640),(1028,1047),(1248,1267)]}
for pn,bands in ann.items():
    im=Image.open(f"pages/p{pn:02d}.png")
    tiles=[im.crop((int(140*s),int((a-14)*s),int(1068*s),int((b+10)*s))) for a,b in bands]
    H=sum(t.size[1] for t in tiles)+10*len(tiles); W=max(t.size[0] for t in tiles)
    out=Image.new("RGB",(W,H),"white"); y=0
    for t in tiles: out.paste(t,(0,y)); y+=t.size[1]+10
    out.save(f"crops/ann_p{pn}.png"); print(pn,out.size)