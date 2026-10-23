b=Image.open("crops/p23_img1.png"); b.crop((280,0,453,200)).resize((173*4,200*4),Image.LANCZOS).save("crops/p23_img1_caption_x4.png")
# also the white + location
b.crop((150,100,260,190)).resize((440,360),Image.NEAREST).save("crops/p23_img1_whiteplus.png")