
chk.to_csv(AUD+'data/f35a_eta_check.csv',index=False)
p_=AUD+'../hydroacoustics-audit-architecture.md'
t=open(p_).read()
reps=[("anti-correlated about about 25–30 Hz","anti-correlated about 25–30 Hz"),
("that range holds 23–24 % of the end-of-flight prior weight","that range holds 22–24 % of the end-of-flight prior weight"),
("- **Reproduction:** `data` check, ≤ 0.02 dB at every station, source depth and τ (C5 PASS).","- **Reproduction:** `data/f35a_eta_check.csv`, ≤ 0.02 dB at every station, source depth and τ (C5 PASS)."),
("(TL at 5 Hz, 10 m source:\n  124.4 dB at 3,342 km,","(TL at 5 Hz, 10 m source:\n  124.4–125.2 dB at 3,342 km,"),
("- **Scored:** 8 shots detected at both H01W and H08S. 13 shot-station spectra were traced.","- **Scored:** 8 shots detected at both H01W and H08S were traced; 13 shot-station spectra gave a usable 50 Hz signal."),
("keeps abs(ln R_hyd) ≤ 0.31","keeps abs(ln R_hyd) ≤ 0.30"),("with abs(ln R) ≤ 0.31","with abs(ln R) ≤ 0.30")]
for a,b in reps:
    assert a in t, a[:40]; t=t.replace(a,b)
open(p_,'w').write(t); print('ok')
