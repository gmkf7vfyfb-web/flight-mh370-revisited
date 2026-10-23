from PIL import Image
p = host.artifact_path('185e31a8-1adc-42fd-9fb6-5d3b6815587d')
im = Image.open(p); print(im.size)
crop = im.crop((int(im.size[0]*0.68), int(im.size[1]*0.44), im.size[0], int(im.size[1]*0.84)))
crop = crop.resize((crop.size[0]*2, crop.size[1]*2))
crop.save('poster_mh370_panels.png')
host.view_image('poster_mh370_panels.png')