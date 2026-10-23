cd gfx && python - <<'E'
s=open('charts_kadri.py').read()
s=s.replace("No multiplicity correction: 120 H01W windows x 4 detectors were \"\n            \"scored and 6 report-level (p <= 0.05) rows are expected by chance; 1 was found.","No multiplicity correction: 30 H01W windows x 4 detectors = 120 tests were \"\n            \"scored; 6 report-level (p <= 0.05) rows are expected by chance and 1 was found (searches note, Table 2).")
s=s.replace('"p-values are per window, without correction for the 480 window tests\\n(120 windows x 4 detectors) at Cape Leeuwin.\\n"','"p-values are per window, without correction for the 120 tests\\n(30 windows x 4 detectors) at Cape Leeuwin; 6 values below 0.05\\nare expected by chance, 1 was found.\\n"')
open('charts_kadri.py','w').write(s)
E
grep -n "120 tests" charts_kadri.py | cut -c1-80