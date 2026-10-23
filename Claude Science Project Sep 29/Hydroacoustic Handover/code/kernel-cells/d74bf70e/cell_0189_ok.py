from PIL import Image
pg=np.array(Image.open("hydro/blackman_p_fig2.png").convert("L")).astype(int)
sub=pg[560:650, 140:500]
dk=sub<110
rws=np.where(dk.sum(1)>200)[0]+560; cls=np.where(dk.sum(0)>50)[0]+140
print("rows",rws,"cols",cls)