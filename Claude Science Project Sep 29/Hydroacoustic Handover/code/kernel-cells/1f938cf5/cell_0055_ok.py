
for r_ in (2,5,10,15,25): print(r_, (Lm.dHX<=r_).sum(), Lm[Lm.dHX<=r_].groupby('stratum').size().to_dict())
