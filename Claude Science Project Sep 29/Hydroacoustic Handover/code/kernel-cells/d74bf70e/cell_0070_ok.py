import numpy as np
from PIL import Image
P="repo/ISO Sept 28 Status/inputs/papers/hydroacoustics/duncan-fig3.png"
im = np.array(Image.open(P).convert("RGB")).astype(int); H,W,_=im.shape; print(H,W)
dark = (im.sum(2) < 200)
# axis spines: long dark runs
rows = np.where(dark.sum(1) > 0.6*W*0.75)[0]; cols = np.where(dark.sum(0) > 250)[0]
print("rows", rows, "cols", cols)
# colours present
from collections import Counter
cnt = Counter(map(tuple, im.reshape(-1,3)))
print([c for c in cnt.most_common(25)])
