cd repo && C="Claude Science Project Sep 29/coordination"
sed -i '' 's|built by\n`prepare/build_path_stub.py`|&|' ../hydro_ot_entry.txt
cat ../hydro_ot_entry.txt >> "$C/OCEAN_TRANSPORT.md"
cat >> "$C/OCEAN_TRANSPORT.md" <<'EOF'
- **As built** (module branch `74d9901`, DOI fixed at `59d834d`): air9 to H01W is 1,662.5 km, with 3,326
  bathymetry samples and 67 profile nodes; air9 to H08S is 3,549.0 km, with 7,099 samples and 142 nodes.
  The stub totals 1.9 MB committed. The WOA box netCDF (1.35 MB) is an artifact only. GEBCO_2026 DOI
  10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa.

— hydroacoustics
EOF
cat >> "$C/architecture.md" <<'EOF'

## 2026-10-09 — hydroacoustics: morning rulings acted on

All seven rulings are done or answered. Analysis ran outside the lock at 2 threads; nothing heavy ran.

1. **Blackman manifest** (`aa46dc7`): `data/blackman/MANIFEST.txt` records the archived `.b64` repair
   without editing it. As committed it is 16,583 characters, sha256 `c01545d7…a72cc7`. Inserting 'G' at
   offset 13597 gives a 12,436-byte zip, sha256 `96b0cb89…70d8f7`, with every CRC passing. I reproduced
   this independently today and it matches the artifact. The Drive copy is marked superseded, and the
   2001 H08S position is marked provisional.
2. **Bearing-mixture rerun** (pre-registered and committed before running, `c3d725f`). The literature
   mixture has a core of 0.5 or 1.0°, tail weight 0.1 or 0.3, a 4° tail, and a 0.5° station bias.
   Under it, **a single site with bearing carries 0.62–1.32 bit**: H01W gives 0.69 / 0.89 / 0.98 / 1.32
   and H08S 0.62 / 0.77 / 0.93 / 1.22 across the four mixtures. That is "modest" in three of four and
   "material" only at the 0.5° core with a 10% tail. The t₃/3.3° reference row reproduces last night's
   figures (0.49 against 0.46; 0.38 against 0.38). Two sites strengthen to 2.38–3.21 bit. **Please
   qualify the headline in amendment 6:** a single site is nearly worthless **for arrival time only**. A
   single triad with a well-measured bearing is modest to material, and the two-site case remains
   the strong one. Whether a 0.5° core is attainable at a marginal SNR is exactly what
   injection-recovery will measure. Artifact `bearing-mixture-rerun.csv`
   (`610384ee-d6d6-496e-bd29-a2f58e7d7d12`).
3. **WOA23 + GEBCO stub built** (`74d9901`), on the two paths only, 1.9 MB committed. Its assumptions
   are stated in `OCEAN_TRANSPORT.md` today, where the new ocean-transport session will see them.
   **Neither path is blocked:** the corridor seafloor never comes within 300 m of the sound-channel axis
   (950–1,150 m, c_min 1,481–1,489 m/s). Both shallowest points (1,483 m and 1,613 m) are at the
   receivers. About 60% (H01W) and 92% (H08S) of path samples sit on GEBCO's satellite-predicted
   depths (TID 40), not soundings.

**Two things for you.**

- **Amendment 2 carries a report error.** Blackman prints air9 to H08S as "about 4825 km" (report text,
  section 4.1). The geodesic from the report's own air9 coordinates to the FDSN H08S position is
  **3,549 km**, while the same paragraph's H01 figure (1,665 km) checks to 2 km (1,662.8). I take the
  4,825 to be wrong in the report and use the geodesic. Please qualify amendment 2.
- **The negative control needs its own paths.** air8 (−23.42, 88.22) to H01 is 2,812 km and to H08S
  is 2,424 km. The approved stub covers air9 only, so as it stands the validation can test air9 but
  not explain the air8 non-detection at H01. **Request:** extend the stub to air8 to H01W and to H08S,
  which is the same size again (about 2 MB). Until you rule, I will do the air9 KRAKEN prediction
  against Fig. 23 and hold air8.

Next: restore the KRAKEN build from its artifact and predict air9 transmission loss at H01W and H08S
over 5–60 Hz against the Fig. 23 chart readings, outside the lock (KRAKEN is single-threaded).

— hydroacoustics
EOF
git add "$C/OCEAN_TRANSPORT.md" "$C/architecture.md" && git commit -q -m "Coordination: hydroacoustics - morning rulings acted on; ocean-transport interface request and stub disclosure"
for i in 1 2 3 4; do
  if timeout 60 git pull -q --rebase origin claude-science-sep29; then timeout 60 git push -q origin HEAD:claude-science-sep29 && { echo pushed; break; }
  else for f in "$C/OCEAN_TRANSPORT.md" "$C/architecture.md"; do python3 - "$f" <<'EOF'
import sys,re; p=sys.argv[1]; t=open(p).read()
t=re.sub(r'^(<<<<<<<|=======|>>>>>>>).*\n','',t,flags=re.M); open(p,'w').write(t)
EOF
done; git add "$C"; GIT_EDITOR=true git rebase --continue >/dev/null; fi; sleep 3; done
grep -c -E '^(<<<<<<<|=======|>>>>>>>)' "$C/architecture.md" "$C/OCEAN_TRANSPORT.md"; git log --oneline -1