for z in ['1','2','3']:
    im=Image.open(f'gistda/resize_area{z}_A1.jpg'); print(z,im.size)
    W,Hh=im.size
    top=im.crop((0,35,W,60)).resize((W*4,100),Image.LANCZOS); top.save(f'gistda/z{z}_top.png')
    left=im.crop((0,60,30,600)); left=left.rotate(-90,expand=True); left=left.resize((left.width*4,left.height*4),Image.LANCZOS); left.save(f'gistda/z{z}_left.png')
    foot=im.crop((0,595,200,700)).resize((800,420),Image.LANCZOS); foot.save(f'gistda/z{z}_foot.png')