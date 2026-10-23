cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
old='''  Statistics (criteria.md definitions):'''
new='''  AMENDMENT 1 (22 Oct 2026 02:50 UTC, before any residual was computed; raised by the reviewer): the band COUNTS
    above were mis-stated. 12.5-63 Hz without 40 Hz is 7 bands, and the audit's H08S rows run 6.3-63 Hz, so H08S
    without 40 Hz is 10 bands. The RULE (Fig. 23 span at the station, intersected with the Fig. 2 readable set) is
    unchanged and is what the code applies; no threshold or definition changed.
  Statistics (criteria.md definitions):'''
assert old in s; s=s.replace(old,new,1); open('tl_recal_block9.py','w').write(s); print('amended')
EOF