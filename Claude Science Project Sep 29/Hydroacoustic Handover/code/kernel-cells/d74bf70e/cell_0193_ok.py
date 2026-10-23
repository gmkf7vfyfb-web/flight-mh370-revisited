cr=pg[600:1300,150:750]; d2=cr<130
for y in range(180,300):
    if d2[y].sum()>250: print("hline", y, d2[y].sum())
cols=[x for x in range(600) if d2[200:290,x].sum()>70]; print("vlines", cols)