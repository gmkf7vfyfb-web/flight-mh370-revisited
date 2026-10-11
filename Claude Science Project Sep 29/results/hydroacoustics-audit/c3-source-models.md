# C3 declaration: airgun source models substituted for Blackman's flat source (before computation)

Declared under criteria.md C3 before any substituted residual is computed. No parameter is fitted to Fig. 23.

Notation: r_b = observed TL − model TL (dB) as in criteria.md. Blackman's observed TL is source level minus
received level, with a source level that is flat over 5–60 Hz (230–240 dB re 1 µPa at 1 m "in the 5~60 Hz range",
printed p. 7, from the near-source hydrophone, Fig. 2). If the source level that actually enters the sound channel
is SL_B + X_b, the corrected residual is r'_b = r_b + X_b.

| id | source model | X_b | basis |
|---|---|---|---|
| M1 | flat (Blackman) | 0 | reproduces the module |
| M2 | Blackman's level already contains the vertical surface ghost; the model adds the ghost again | −20 log10 abs(2 sin(k z_s)), z_s = 10 m (9, 12 m as range) | free-surface image of a point source; the module's sensitivity row |
| M3 | horizontal directivity of a planar 4-string array; Blackman's level is the coherent (vertical) level | 10 log10 D_b, D_b = azimuth-mean, band-mean abs(AF)²/N² at elevation 0° and 10° | geometry: 4 strings × 5 guns on a 24 m × 16 m footprint. This is the L-DEO 4-string layout as described for R/V Langseth in the NSF/L-DEO environmental assessments (2009), used as a proxy because the Ewing 20-gun geometry is not printed in Blackman (2004). That such arrays radiate less sound in near-horizontal directions is stated in the NMFS notice for the L-DEO Langseth surveys (Federal Register document 2012-07717, public-inspection copy, p. 10: effective source levels for horizontal propagation "are lower than those for downward propagation"; text read in the audit) |
| M4 | M2 and M3 together | sum | |

Pass rule (C3): SUPPORTED if any of M2–M4 gives abs(slope) ≤ 3 dB/oct at both H01W and H08S without making the
level FAIL; otherwise NOT SUPPORTED. The H08S bands below 12.5 Hz are reported separately, because Fig. 23 has air9
data there only at H08S (5.4–12.7 Hz), which the module's brief did not use.

*Architecture audit, 2026-10-10.*

**Amendment 1 (same day, after a reviewer finding; no number changed).** The first version cited Tolstoy et al. (2004) for
the statement that airgun arrays focus energy downwards. The audit never obtained that paper's text from an authorised
source (the open-access fetch failed), so the citation is withdrawn and replaced with the public NMFS Federal Register
notice 2012-07717. M3 itself (geometry and formula) is unchanged.

**Amendment 2 (same day).** Amendment 1's citation was first taken from a search listing. The notice was then
retrieved (public-inspection PDF, 82 pages) and the statement was confirmed on its page 10. No number changed.

Retrieved file: public-inspection.federalregister.gov/2012-07717.pdf, sha256 4183cde543bd656cca92494c9dacfa3229394fe03219d5762407d1258301abb5; statement on its page 10.
