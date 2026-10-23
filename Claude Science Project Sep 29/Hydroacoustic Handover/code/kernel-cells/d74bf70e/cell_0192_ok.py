print(pg.shape, (pg<120).sum(1)[600:1300:25])
Image.fromarray(pg[600:1300, 150:750].astype(np.uint8)).save("hydro/fig2_crop.png")