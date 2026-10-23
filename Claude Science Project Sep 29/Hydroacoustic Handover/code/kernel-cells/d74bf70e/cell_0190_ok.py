dk=pg<120
reg=dk[540:680, 180:520]
r=reg.sum(1); c=reg.sum(0)
print("row maxima", sorted([(int(v),i+540) for i,v in enumerate(r)], reverse=True)[:6])
print("col maxima", sorted([(int(v),i+180) for i,v in enumerate(c)], reverse=True)[:6])