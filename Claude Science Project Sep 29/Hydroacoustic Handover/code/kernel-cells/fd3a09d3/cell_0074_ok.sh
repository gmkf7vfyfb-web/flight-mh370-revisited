cat > /tmp/note_numbers.py <<'EOF'
import pandas as pd, numpy as np, json, sys
T=sys.argv[1]; EV=sys.argv[2]
g=pd.read_csv(f'{T}/tl_grid.csv.gz', dtype={'receiver':str}); g10=g[g.src_depth_m==10]
print('## grid size'); print('sources', g.source_id.nunique(), 'paths', len(g.drop_duplicates(['source_id','receiver'])), 'rows', len(g), 'offsets', sorted(g.offset_nm.unique()))
print('\n## blocked share per receiver (10 m source, all offsets): share of (path,band) rows not ok')
st=g10.groupby('receiver').status.value_counts(normalize=True).unstack(fill_value=0).round(3); print(st.to_markdown())
print('\n## blocked share per receiver, offset 0 only')
print(g10[g10.offset_nm==0].groupby('receiver').apply(lambda x: round(1-(x.status=='ok').mean(),3)).to_markdown())
print('\n## paths fully blocked (all 10 bands) per receiver, by offset')
pb=g10.groupby(['receiver','offset_nm','source_id']).apply(lambda x:(x.status!='ok').all()).groupby(['receiver','offset_nm']).mean().unstack().round(2); print(pb.to_markdown())
print('\n## TL range on the arc line (10 m, ok rows), 5 Hz / 20 Hz / 40 Hz, min-max dB (raw KRAKEN)')
a=g10[(g10.offset_nm==0)&(g10.status=='ok')]
for rec,h in a.groupby('receiver'):
    print(rec, {fc:(round(h[h.fc_hz==fc].tl_db.min()),round(h[h.fc_hz==fc].tl_db.max())) for fc in (5.0,20.0,40.0)}, 'ok lat span', (h.src_lat.min(), h.src_lat.max()))
print('\n## comparison summary'); print(pd.read_csv(f'{T}/comparison_summary.csv').round(2).to_markdown(index=False))
c=pd.read_csv(f'{T}/comparison_old_vs_new.csv'); s=c[(c.check=='same_point_same_method')].dropna(subset=['delta_db'])
print('\n3376 same-point deltas by band (max abs):'); print(s[s.receiver=='3376'].groupby('fc_hz').delta_db.apply(lambda x: round(x.abs().max(),2)).to_dict())
print('max abs excluding 3376:', round(s[s.receiver!='3376'].delta_db.abs().max(),2))
w=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None
print('\n## detectable by band (ridge excluded), frac_pd')
tb=pd.read_csv(f'{EV}/detectable_by_band.csv'); tb=tb[tb.ridge_points=='excluded']
print(tb.pivot_table(index=['receiver','eta'],columns='lat_band',values='frac_pd').round(3).to_markdown())
print('\n## above noise median (ridge excluded)')
print(tb.pivot_table(index=['receiver','eta'],columns='lat_band',values='frac_above_noise_median').round(3).to_markdown())
ev=pd.read_csv(f'{EV}/evidence_alone.csv', dtype={'receiver':str}); e=ev[(ev.offset_nm==0)&(ev.eta==1e-4)&(~ev.ridge_source)]
print('\n## received SPL at E median, eta=1e-4, min/max over arc per receiver vs noise median')
print(e.groupby('receiver').agg(spl_min=('spl_at_E_q50','min'), spl_max=('spl_at_E_q50','max'), noise=('noise_median','first')).round(1).to_markdown())
src=pd.read_csv(f'{T}/../raw/passA/sources.csv') if False else None
EOF
pip list 2>/dev/null | grep -i tabulate || echo "no tabulate"