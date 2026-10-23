for n in ['mh370_3.jpg','area2_A1.jpg']:
    b=open('gistda/'+n,'rb').read(); print(n,b[:20])
    try:
        im=Image.open('gistda/'+n); print(im.size,im.mode); im.convert('RGB').save('gistda/'+n.replace('.jpg','_c.png'))
    except Exception as e: print(e)