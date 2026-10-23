Hs=gaussian_filter(condH,1.0); Hs/=Hs.sum()
postn=Hs; lvP=[hpd_level(postn,q) for q in (0.9,0.5)]          # chart2 reads these globals
src2b=inspect.getsource(chart2).replace("impact PDF if the Pleiades objects are debris, 50 % / 90 % (dashed)","impact PDF conditional on the Pleiades objects being debris, 50 % / 90 % (dashed)") \
  .replace("Pleiades: run J map-D0 'post' (flight-only cell mass conditional on H, q = 1/3, C2 silent, 0.05 deg).",
           "Pleiades: run J flight-only cell mass (map-D0, q = 1/3, C2 silent) x headline likelihood (joint surface rho 0.25, GlobCurrent relative windage, two-model mean), 0.05 deg, smoothed 1 cell; mean 35.44 S 92.20 E (module README 35.38-35.60 S 92.20-92.62 E; composer core x Pleiades 35.43 S 92.19 E).")
exec(src2b)
new2={k:chart2(k) for k in CANDS}
for k,cd in CANDS.items():
    mm=(np.abs(LA-cd['lat'])<=1)&(np.abs(LO-cd['lon'])<=1/np.cos(np.radians(cd['lat'])))
    print(k, 'conditional-on-H mass within 1 deg', round(float(condH[mm].sum()),3), ' inside 50% region:', bool(Hs[np.argmin(abs(plat-cd['lat'])), np.argmin(abs(plon-cd['lon']))]>=lvP[1]))