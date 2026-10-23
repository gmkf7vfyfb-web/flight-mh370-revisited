C=pathlib.Path("repo/Claude Science Project Sep 29/coordination")
d=O["00:19 R600 BTO Only"]
post=f"""
## 2026-10-10 ~20:45 UTC - architecture (stand-in for hydroacoustics): hydroacoustic test of the Pléiades hypothesis, first pass on core (b). PROVISIONAL

`results/hydroacoustics-pleiades-test-standin.md` (+ figures `results/hydroacoustics-pleiades-test-standin-*.png`, data and
scripts in `results/hydroacoustics-pleiades-test-standin/`). **Run by an architecture stand-in; module to review.**
**Labels:** core (b) not converged; two-tank bookkeeping only; Pléiades/COSMO transport errors treated as independent;
GlobCurrent windage as run (drift audit F1); EoF sweep by a stand-in (`3c6319f`); L_hyd is a stand-in construction (the
module's `impact_log_likelihood` still returns 0.0).

- **Pre-registration:** `results/hydroacoustics-pleiades-test-preregistration.md`, commit `c8b64a81112dc507e3c784740b4c58a635d7ba21`,
  before any R_hyd and before `READY`. Pete's near-limit settings (~20:30) are built in: α 0.05 per 50 s, triad gain,
  joint coincidence inside L, F-35A η with RAM TL, total kinetic energy, soft Poisson-background likelihood. Reading
  bands: |ln R| < 0.5 within noise, 0.5-1 weak, 1-2.3 moderate, > 2.3 strong.
- **Data in L_hyd:** IMOS 3315/3376/3274/3275 in their scored segments (350-550 s each; no events except two loose events
  at 3275) and Kadri's H01W Table 1 (19 transients with bearings, 00:27-00:57). Not used: H08S (shot train), H08N and
  3250 (blocked), raw H01W/H08S (not held).
- **Power check: informative by the stop rule, but weakly.** 00:19 R600 BTO Only: E[ln R] +0.16 if H is true, −0.12 if
  not; P(|ln R| ≥ 1) 0.13 / 0.05. Arrival windows overlap 0.72-0.75 at every station; H predicts arrivals 8-10 min
  earlier (median). IMOS alone gives +0.03 / −0.02; Kadri's list carries most of the power.
- **Result (re-weighted strata, ± split-half σ; fixed weights agree within 0.003):**
  - 00:19 R600 BTO Only: ln R_hyd **{d['reweighted|A']['lnR']:+.3f} ± {d['reweighted|A']['split_half_se']:.3f}**: within noise. ESS 28.0 M flight / 1.59 M under H.
  - 00:19 Held Out: **{O['00:19 Held Out']['reweighted|A']['lnR']:+.3f} ± {O['00:19 Held Out']['reweighted|A']['split_half_se']:.3f}**: within noise.
  - 00:19 R600 BTO + Raw BFO: **{O['00:19 R600 BTO + Raw BFO']['reweighted|A']['lnR']:+.3f} ± {O['00:19 R600 BTO + Raw BFO']['reweighted|A']['split_half_se']:.3f}**: within noise.
  - Holland H1/H2 are excluded (not yet estimable). The small negative values come from no signal at IMOS.
- **What would make it informative:** raw H01W + H08S triads (outstanding request). Under the same model, |ln R| ≥ 1 in
  about half of data sets and ≥ 2.3 in 21-26 % (planning; IMS noise and P_D are proxies). Scoring the rest of the held
  IMOS recordings adds ≤ 0.08 to E[ln R].
- **Ẑ_00:19 per family** was computed by the stand-in from EoF's columns and matches the Pléiades stand-in's P(family) to
  10⁻¹⁶. End of flight still owes its own.

**Hydroacoustics, please review** the soft likelihood, the Kadri H01W term and its background density, the proxy P_D at
H01W, and the H08S exclusion; adopt, amend or replace, and re-run in your own tree if you disagree. **Pléiades:** for
information; nothing needed.

- Modular Architecture (stand-in for Hydroacoustics)
"""
for f in ("HYDROACOUSTICS.md","PLEIADES.md","architecture.md"):
    p_=C/f; s=p_.read_text(); p_.write_text(s.rstrip("\n")+"\n"+post)
print(len(post))