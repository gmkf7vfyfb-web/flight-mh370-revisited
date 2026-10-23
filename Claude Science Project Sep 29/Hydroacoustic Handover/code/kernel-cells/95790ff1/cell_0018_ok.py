from PIL import Image
os.makedirs("crops",exist_ok=True)
for pn in range(27,34):
    im=Image.open(f"pages/p{pn:02d}.png"); W,H=im.size
    im.crop((int(W*0.1),int(H*0.12),int(W*0.9),int(H*0.5))).save(f"crops/p{pn}_top.png")
    im.crop((int(W*0.1),int(H*0.5),int(W*0.9),int(H*0.9))).save(f"crops/p{pn}_bot.png")
print(W,H)