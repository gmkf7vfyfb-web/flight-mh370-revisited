cd /tmp
python - <<'EOF'
import pathlib; p=pathlib.Path('/tmp/note_numbers.py'); s=p.read_text()
s=s.replace("print(rec, {fc:(round(h[h.fc_hz==fc].tl_db.min()),round(h[h.fc_hz==fc].tl_db.max())) for fc in (5.0,20.0,40.0)}, 'ok lat span', (h.src_lat.min(), h.src_lat.max()))",
"print(rec, {fc:(h[h.fc_hz==fc].tl_db.min().round(0),h[h.fc_hz==fc].tl_db.max().round(0), int(h[h.fc_hz==fc].tl_db.notna().sum())) for fc in (5.0,20.0,40.0)}, 'ok lat span', (h.src_lat.min(), h.src_lat.max()))")
p.write_text(s)
EOF
python /tmp/note_numbers.py /tmp/tlg_tables_AB /tmp/tlg_ev_AB 2>&1 | sed -n 30,200p