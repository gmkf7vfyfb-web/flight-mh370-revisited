# Fig. 10.3 vector recovery (18 Oct 2026, core)

`fig10-3-top-bto-only-vector.csv` and `fig10-3-bottom-bto-bfo-vector.csv` are the curves of Davey et al. (2016) Fig. 10.3,
read from the PDF vector paths (results/davey-2016.pdf, sha256 37554ca5..., page index 101) with pymupdf. They are not hand-digitised.
Calibration comes from the axis tick marks. The overlay check image shows the recovered points on the rendered page.

| Panel | median | 95% interval | mass 34.5-36.5 S | note |
|---|---|---|---|---|
| bottom (BTO+BFO), vector | 37.458 S | 39.233-34.843 S | 0.261 | peak 0.352 |
| bottom, old hand CSV (fig10-3-bfo-latitude-pdf.csv) | 37.557 S | 39.403-34.928 S | 0.2406 | overlap with vector 0.958 |
| top (BTO only), southern part renormalised | 38.901 S | 40.546-35.989 S | 0.098 | tip clipped at the 0.4 frame, 39.34-39.11 S (about 0.006 of area); 0.886 of mass is south of 0; northern mode near 45 N |

PROPOSAL (needs Pete's agreement): use the vector bottom curve as the project's Davey reference in place of the hand CSV.
