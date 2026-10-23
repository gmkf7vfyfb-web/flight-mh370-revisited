eofc = cfg["hypotheses"]["end-of-flight"]
flat = json.dumps(eofc)
print("EoF config mentions of 'engine':", re.findall(r'"[^"]*engine[^"]*"', flat))
print("EoF config mentions of 'tank'/'asym'/'yaw':", re.findall(r'"[^"]*(?:tank|asym|yaw|rudder)[^"]*"', flat))
# is the 2000 kg fallback being used? a uniform fallback would put a spike at a single lead time
lead = fo - tk
A = (fam4==1.0)|(fam4==2.0)
print("\nA-family: takeover-minus-flameout (s) q01..q99:", [round(x,2) for x in wq(tk[A]-fo[A], wn[A], (0.01,0.25,0.5,0.75,0.99))])
dry_at_ho = tk < 660
print("distinct realised flame-out times:", len(np.unique(fo[np.isfinite(fo)])))
h,b = np.histogram(fo[np.isfinite(fo)], bins=np.arange(659,2400,30), weights=wn[np.isfinite(fo)])
top = np.argsort(h)[-3:][::-1]
print("heaviest 30-s flame-out bins (UTC, share):", [(hhmm(b[i]), round(float(h[i]/h.sum()),4)) for i in top])
print("fallback-implied flame-out if 2000 kg at 5,764 kg/h from 00:11:", hhmm(659+2000/5764*3600))
