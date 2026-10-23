z=np.load(GD/"map_D0.npz"); s=z["snr_best_eta1"]-30; lat=z["lat"]
for lo,hi in [(-26,-25),(-25,-24),(-24,-22),(-22,-20)]:
    m=(lat>lo)&(lat<=hi); print(lo,hi,m.sum(), np.percentile(s[m],[5,50,95]).round(1), np.bincount(z["best"][m],minlength=8))
print(RL.RECEIVERS)