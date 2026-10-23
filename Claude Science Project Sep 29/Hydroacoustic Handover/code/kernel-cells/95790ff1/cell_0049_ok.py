def band(img,x0,y0,x1,y1): return img.crop((x0,y0,x1,y1)).copy()
L=255
a3row=band(p26,L,1150,2250,1215); a4row=band(p26,L,1555,2250,1620)
t5=band(p26,L-5,y0,2250,y0+575)
d=ImageDraw.Draw(t5); d.rectangle((0,372,1995,430),outline=(220,0,0),width=6); d.rectangle((0,432,1995,478),outline=(0,90,220),width=4)
p29=Image.open("pages/p29.png").convert("RGB"); W29,H29=p29.size
b4=band(p29,int(0.11*W29),int(0.07*H29),int(0.89*W29),int(0.6*H29))   # panel grid incl A4sus3 row
b4cap=band(p29,int(0.11*W29),int(0.64*H29),int(0.89*W29),int(0.7*H29))
p28=Image.open("pages/p28.png").convert("RGB"); W28,H28=p28.size
b3cap=band(p28,int(0.11*W28),int(0.79*H28),int(0.89*W28),int(0.82*H28))
font=ImageFont.load_default()
def lab(text,w):
    im=Image.new("RGB",(w,60),"white"); ImageDraw.Draw(im).text((10,15),text,fill=(0,0,0),font=ImageFont.load_default(size=34) if hasattr(ImageFont,'load_default') else font); return im
parts=[(lab("UCRL-TR-207323 pdf p26 (printed p24) Table 3 row: single sphere at site A3, JD143",2000),None),(a3row,None),
       (lab("pdf p26 Table 4 row: five-sphere at site A4, JD144 10:23:11.56",2000),None),(a4row,None),
       (lab("pdf p26 Table 5 (SUS): red = row printed 'A3' (JD144 10:54:57.77, 915 m); blue = A4 610 m",2000),None),(t5,None),
       (lab("pdf p28 (printed p26) Figure B3 caption: site A3 = single-sphere only",2000),None),(b3cap,None),
       (lab("pdf p29 (printed p27) Figure B4: site A4 panels A4sus2 / A4sus3 / A4sph5 and caption",2000),None),(b4,None),(b4cap,None)]
ims=[p for p,_ in parts]; Wm=max(i.size[0] for i in ims)
ims=[i if i.size[0]==Wm else i.resize((Wm,int(i.size[1]*Wm/i.size[0]))) for i in ims]
Hm=sum(i.size[1] for i in ims)+8*len(ims); comp=Image.new("RGB",(Wm,Hm),"white"); yy=0
for i in ims: comp.paste(i,(0,yy)); yy+=i.size[1]+8
comp.save("out/jd144_check_crop.png"); print(comp.size)