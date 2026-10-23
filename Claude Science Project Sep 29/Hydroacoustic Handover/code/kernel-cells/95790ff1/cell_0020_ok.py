for pn,bands in ann.items():
    im=Image.open(f"pages/p{pn:02d}.png")
    tiles=[im.crop((int(140*s),int((a-2)*s),int(1068*s),int((b+24)*s))) for a,b in bands]
    H=sum(t.size[1] for t in tiles)+10*len(tiles); W=max(t.size[0] for t in tiles)
    out=Image.new("RGB",(W,H),"white"); y=0
    for t in tiles: out.paste(t,(0,y)); y+=t.size[1]+10
    out.save(f"crops/ann2_p{pn}.png")
# stack all pages into two images
imgs=[Image.open(f"crops/ann2_p{pn}.png") for pn in ann]
def stack(lst,fn):
    H=sum(i.size[1] for i in lst)+20*len(lst); out=Image.new("RGB",(lst[0].size[0],H),"white"); y=0
    for i in lst: out.paste(i,(0,y)); y+=i.size[1]+20
    out.save(fn); print(fn,out.size)
stack(imgs[:4],"crops/obs_A.png"); stack(imgs[4:],"crops/obs_B.png")