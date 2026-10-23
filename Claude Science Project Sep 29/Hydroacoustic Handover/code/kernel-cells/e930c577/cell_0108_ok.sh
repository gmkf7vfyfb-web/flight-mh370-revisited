cd leg; python - <<'E'
s=open('README.md').read()
a="**Not consistent at the airframe anchor.** The rows that produce Kadri's arrival at the right time need a coupling 85-340\ntimes the F-35A anchor (19-25 dB). They need 2-9 times the anchor even with the TL 2 sd favourable."
assert a in s
s=s.replace(a,"**Not consistent at the airframe anchor.** The rows that produce Kadri's arrival at the right time need a median coupling of\n0.91 (T) and 0.24 (C). That is about 340 and 90 times the F-35A anchor (25 and 20 dB). Even with the TL 2 sd favourable,\nthey need 9 and 2 times the anchor.")
b="In the exploratory C fit, using Royer's H01W pick moves the point\n  by 15-31 km and leaves it inside L either way."
assert b in s
s=s.replace(b,"In the exploratory C fit, using Royer's H01W pick instead\n  (with or without the 16 s) puts the point 15-31 km from the crossing, inside L either way.")
s=s.replace("about 0.0065 (log10 -2.2) for T and 0.065 (log10 -1.2) for C","about 0.0065 (log10 -2.2) for T and 0.064 (log10 -1.2) for C")
open('README.md','w').write(s)
E
grep -c "" README.md