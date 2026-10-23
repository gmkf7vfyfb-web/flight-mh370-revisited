reg=dk[780:920, 200:720]
r=reg.sum(1); c=reg.sum(0)
print("rows", [(int(v),i+780) for i,v in enumerate(r) if v>300])
print("cols", [(int(v),i+200) for i,v in enumerate(c) if v>80])