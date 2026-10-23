from PIL import Image
im=Image.open('mrsa_p2_img.jpeg'); w,h=im.size
crop=im.crop((530,440,950,675)); crop=crop.resize((crop.width*3,crop.height*3),Image.LANCZOS); crop.save('mrsa_table_zoom.png'); print(crop.size)