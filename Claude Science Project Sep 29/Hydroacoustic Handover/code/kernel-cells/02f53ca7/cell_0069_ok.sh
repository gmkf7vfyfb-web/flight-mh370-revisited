cd "repo/Claude Science Project Sep 29/results"; python - <<'EOF'
p='hydroacoustics-blackman-validation.md'; s=open(p).read()
old='| coupled-mode (RAM) check on the geodesic and the +20 km path, 31.5 and 40 Hz | see the RAM line below |'
new='''| coupled-mode (RAM, parabolic equation; amendment 3, exploratory) — geodesic / +20 km / +50 km, 31.5–63 Hz, no absorption in either model | **+19.1 / +15.7 / +18.1** (geodesic by band 21.6, 20.6, 17.3, 17.6) |'''
assert old in s; s=s.replace(old,new)
old2='''**Verdict under the pre-registered rule: NOT REPRODUCED.** Neither the corridor nor any path within ±20 km comes within
10 dB; clearing the ridge altogether (+40 to +50 km, about seven Fresnel half-widths off the geodesic, which would need
horizontal refraction, not diffraction) still leaves about 25 dB.'''
new2='''**Verdict under the pre-registered rule: NOT REPRODUCED.** Neither the corridor nor any path within ±20 km comes within
10 dB; clearing the ridge altogether (+40 to +50 km, about seven Fresnel half-widths off the geodesic, which would need
horizontal refraction, not diffraction) still leaves about 25 dB. **The RAM check changes the reading of G22:** with mode
coupling the ridge on the geodesic costs only a few dB (RAM is 27–56 dB below the adiabatic KRAKEN on that path, against
−5 to +0.4 dB on the open air9 path and −4 to −10 dB on the ridge-clearing +50 km path), and the excess settles at 15–20 dB
on every path, ridge or no ridge. So the adiabatic model's ridge blockage is overstated by 35–55 dB here (as on air8, where
RAM gave 18 dB against KRAKEN's 39 dB), and the part of G22 that is "the ridge" is explained; a path-wide 15–20 dB excess
remains that neither model closes.'''
assert old2 in s; s=s.replace(old2,new2)
old3='''**Proposed G22 status line (for the architect; ARCHITECTURE.md not edited here):** "G22 still open: air7 → H01W
single-section, N×2D corridor and ±20 km 3-D-proxy TL exceed the observed air7 ≈ air9 level by 57 / 55 / 37 dB (median
31.5–63 Hz); clearing the ridge (+40–50 km) still leaves ~25 dB; the observation may be a noise-selected ceiling.
Next: coupled-mode/3-D model, and Kadri's archive for the 2001 shots."'''
new3='''**Proposed G22 status line (for the architect; ARCHITECTURE.md not edited here):** "G22 partly explained, still open:
the air7 → H01W ridge loss is an adiabatic-model artefact (KRAKEN 57 dB excess on the geodesic, N×2D 55, ±20 km proxy 37;
RAM coupled modes 19 dB on the geodesic, 16–18 dB on paths beside or clear of the ridge); a path-wide 15–20 dB excess over
the observed air7 ≈ air9 level remains in both models, most likely a noise-selected ceiling in Fig. 23 (air7 weak at Cape
Leeuwin; only shots > noise + 3 dB plotted) and/or near-source loss at the air7 site on the Ninetyeast Ridge flank.
Consequence for MH370: ridge/sill blockage from the adiabatic chain is an upper bound on loss; RAM Δ is the correction.
Next: Kadri's archive for the 2001 shots (air7 SNR), and RAM in place of adiabatic KRAKEN on sill-crossing paths."'''
assert old3 in s; s=s.replace(old3,new3)
old4='''The Digitisation track's folder (`results-data/digitised/brown2026/`) was polled every 30 min;
status at the final poll is recorded at the end of this addendum.'''
new4='''The Digitisation track reached the same finding independently (`prepare/digitise_brown_2026.py`, commit
`9854c72`: "the paper contains NO F-35A waveform or spectrum ... has to come from Metz et al., which is NOT held (GAP)"),
so polling stopped at 03:10 UTC (polls 02:30, 02:45, 03:10) rather than at hour 3: nothing could arrive from this source.'''
assert old4 in s; s=s.replace(old4,new4)
old5='''- **Gaps and status:** G22 still open (above).'''
new5='''- **Gaps and status:** G22 partly explained (ridge = adiabatic artefact), still open for the path-wide 15–20 dB (above).'''
assert old5 in s; s=s.replace(old5,new5)
open(p,'w').write(s); print('updated')
EOF