
print(wj.get("notes","")[:300]); print({k:wj[k] for k in wj if k not in("depth_m","notes")})
for k in range(0, nz, 6): print(z[k], round(c[k],1), round(sa[k],2), round(ct[k],2))
# check against neighbouring cells / other orientation
print("alt orientation (lat flipped):", np.round(C[:5, wj["nlat"]-1-i, j],1))
