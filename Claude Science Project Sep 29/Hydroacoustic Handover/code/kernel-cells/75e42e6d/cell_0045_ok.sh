cd src/mdl; python - <<'EOF'
import docx, glob, csv
for f in sorted(glob.glob('ReadMe*.docx')):
    d=docx.Document(f); print('=====',f); print('\n'.join(p.text for p in d.paragraphs if p.text.strip()))
d=docx.Document('Lepas_supplemental_Commons.docx'); t=[p.text for p in d.paragraphs if p.text.strip()]
print('===== SUPPLEMENT paragraphs', len(t), 'tables', len(d.tables))
for p in t[:60]: print('|',p[:300])
for i,tb in enumerate(d.tables): print('TABLE',i, len(tb.rows),'x',len(tb.columns), [c.text[:30] for c in tb.rows[0].cells])
EOF
head -3 Isotope_day_interpolate.csv; tail -3 Isotope_day2.csv; cut -d, -f1 Isotope_day2.csv | sort -u | head