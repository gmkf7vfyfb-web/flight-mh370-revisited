import numpy as np
from PIL import Image
im=np.array(Image.open(host.artifact_path("99b55187-e5c8-4c37-abff-0482499b5a7f")).convert("L")).astype(int)
H,W=im.shape; print(H,W)
dark=im<100
rows=np.where(dark.sum(1)>0.7*W*0.8)[0]; cols=np.where(dark.sum(0)>0.25*H)[0]
print("long rows",rows); print("long cols",cols)