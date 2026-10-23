def crop_frac(pn,box,fn):
    im=Image.open(f"pages/p{pn:02d}.png"); W,H=im.size
    im.crop((int(W*box[0]),int(H*box[1]),int(W*box[2]),int(H*box[3]))).save(fn)
crop_frac(25,(0.1,0.16,0.83,0.5),"crops/t1_a.png")
crop_frac(25,(0.1,0.5,0.83,0.83),"crops/t1_b.png")
crop_frac(26,(0.1,0.08,0.87,0.52),"crops/t25_a.png")
crop_frac(26,(0.1,0.56,0.87,0.88),"crops/t25_b.png")