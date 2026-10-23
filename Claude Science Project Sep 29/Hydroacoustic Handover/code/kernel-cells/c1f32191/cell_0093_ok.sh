O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; python - <<'EOF'
p="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/README.txt"; s=open(p).read()
warn = """*** WARNING (23 Oct 2026, amendment A4): THE COLUMNS IN THIS DIRECTORY ARE ON THE OLD IMOS TL TABLE (imos_tl_ramcorr_arc.csv, constant
*** rule-2 RAM correction, gap G-TL1). The RAM-along-grid track has since issued the corrected table imos_tl_ram_arc.csv (run-j-tl-grid/tables/).
*** The per-row columns here MUST BE REWRITTEN with the corrected table before any composer use. They are internally consistent with this
*** README and READY stays. The corrected STATISTICS (upper limits, evidence, Bayes factors; not columns) are in stats-ramgrid/ and in the
*** addendum of results/hydroacoustics-composition-run-j.md. Rewrite recipe: python driver.py (writes to run-j-gated.staging, ~6.3 GB, needs >= 28 GiB free).

"""
if "amendment A4" not in s: open(p,"w").write(warn + s)
print(open(p).read()[:400])
EOF
cat $O/READY