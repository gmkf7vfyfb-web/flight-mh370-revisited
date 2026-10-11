
## Amendment 1: the published 20-gun layout (pre-registered d994b013; results deb70727)
- **Source:** USGS Open-File Report 95-228 (Brocher et al. 1995, doi:10.3133/ofr95228), PDF p. 70, Fig. 4. The
  vector text gives 20 gun IDs, volumes summing to **8,470 in³** (EW0112: 8,465), and positions in three rows
  15 ft apart along track, 34 m across.
  - Volumes 145–875 in³; table in `ewing_20gun_layout_ofr95228.csv`.
  - This is the 1994 configuration, used as the best available and DECLARED.
- **H-ref and H-flat with this layout:** both stations stay within slope ≤ 3 dB/oct in **0 %** of the 45 geometries,
  with equal weights and with V^(1/3) weights. Both remain **NOT SUPPORTED**.
- **Far-field directivity (diagnostic):**
  - Ship heading on air9 is 111.2°. The bearings to H01W (123.0°) and H08S (303.4°) are both about 12° off the tow
    axis.
  - The array factor is −0.2 dB at 12.5 Hz, −1.5 dB at 31.5 Hz and −6.5 dB at 63 Hz.
  - A point-source model therefore over-predicts the high bands. This alone adds about +2.7 dB/oct to the residual.
- **POST HOC (exploratory, found after seeing the data; not a verdict):** H-flat + near-field Ball factor + far-field
  array factor puts both stations within slope ≤ 3 dB/oct in **78 %** of geometries. At the nominal geometry the
  slopes are +2.3 dB/oct (H01W, PARTIAL) and −0.4 dB/oct (H08S, PASS).
  - This is a candidate explanation of the airgun tilt: Blackman used a flat source level, and the array has
    horizontal directivity.
  - It must be confirmed on independent airgun sites with other headings (air1–air5 → H08N, air7/air8 → H08S).
    That test is pre-registered next, before any of those curves is digitised.
