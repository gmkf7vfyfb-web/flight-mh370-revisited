# The size response g_k(W): implemented, and where it changes anything

10 October 2026, searched-areas module. `engine/hypotheses/seabed-search/lib.rs`; five new tests.
Specification: `results/seabed-detectable-target.md` §§3–6. Brief §3 asked for this before settling's
fields arrive, with a point-target placeholder meanwhile.

## What landed

The likelihood is now

    M_k(W) = 1 − c_k(y) · g_k(W) · q_k,     g_k(W) = 1 − Π_i [1 − a_k(L_i, h_i)]

with `a_k` the log-normal response of §4, in the ratio of the feature extent — the larger of the
acoustic shadow `S = h R / (H − h)` and the plan length `L` — to `m` resolution cells:

    a_k(L, h) = mean over ground range R of Φ( ln( max(S, L) / (m · Δ_k(R)) ) / s_k )

`Δ_k(R)` is the coarser of the along-track and across-track cells. Along-track is `R·θ` for
real-aperture side-scan and `D/2` for synthetic aperture, independent of range — the operational
difference between the deep-tow and the SAS layers. Across-track is the slant cell projected by the
grazing angle, `Δr·√(R²+H²)/R`, so it degrades *towards* nadir. A piece's across-swath position is
unknown, so the response is averaged over the usable swath on a 32-point rule. `m = 3` by default
(literature practice is about 2 for detection, 3–5 for recognition) and `s_k = 0.5`.

`FieldCoverage` implements §5: `Coarse` (default, the field is inside valid data as a whole) and
`Fine` (each piece independently), reported beside it.

**No existing result changes.** A campaign with no `sensor` block scores a point target, `g_k = 1`,
and `mh370 evaluate` on `runs/fixture-8/bto-bfo/seed-5` with the Ocean Infinity 2018 override is
**byte-identical** to the pre-change build (mean ln P(no find) −1.3604486856782074 either way).
`run.toml` carries no sensor geometry and is unchanged.

## Where the model earns its place

The §6 prediction — that `g_k` saturates for anything settling is likely to produce, so the result is
set by coverage and ρ — is now a test rather than an argument. Against illustrative side-scan geometry
(100 m altitude, 0.3° horizontal beamwidth, 0.15 m slant cell, 40–400 m swath; **plausible values
stated as such, not published specifications** — the only sensor datum verified in primary form is
Bluefin-21/*Artemis*, 120 kHz at a 400 m range scale and 45 m altitude, ATSB 2017 printed p. 42):

| field | g_k | reading |
|---|---|---|
| 40 pieces, 0.5–8.3 m long, 0.1–2.05 m proud | **> 1 − 10⁻⁹** | the realistic case; indistinguishable from a point target |
| one piece 20 m long, 4 m proud | 0.98–0.99 | a single piece does not quite saturate, because the far-swath cell is coarse |
| 40 fragments 0.12 m long, 0.02 m proud | **< 0.5** | the regime where the target model bites |

So the boundary sits roughly three orders of magnitude in piece size below anything an aircraft
breakup produces. **This is a negative result and it is worth keeping**: it says the module's
uncertainty budget belongs to ρ and to the coverage rasters, that effort spent refining the piece-size
distribution will not move the posterior, and that every run made with the point-target placeholder is
valid rather than provisional — it is the saturated limit of the full model, not a crude stand-in.

Two caveats on that. The second regime of §6 — a field whose extent rivals the coverage-gap scale, so
that `Coarse` and `Fine` separate — is **not** settled by this, and the `Fine`/`Coarse` gap stays a
labelled sensitivity. And the sensor parameters above are illustrative; when settling delivers fields
the campaign blocks need real geometry, which for the Phase 2 systems is not in any source read so
far.

## What is still owed

- Real per-campaign sonar geometry, or an explicit statement that it is unavailable and the point
  target is therefore the reported model.
- Settling's wreckage samples in place of the placeholder, with their draws **averaged**, never
  multiplied.
