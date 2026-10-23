f=np.asarray(Image.open("crops/p23_img0.png").convert("L")).astype(int)
H,W=f.shape
dark=f<100
rows=[y for y in range(H) if dark[y].sum()>0.7*W*0.8]
cols=[x for x in range(W) if dark[:,x].sum()>0.6*H*0.8]
print(H,W,rows,cols)