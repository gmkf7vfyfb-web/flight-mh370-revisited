cd /tmp
python - <<'EOF'
import pathlib; p=pathlib.Path('/tmp/note_numbers.py'); s=p.read_text()
s=s.replace("(h[h.fc_hz==fc].tl_db.min().round(0),h[h.fc_hz==fc].tl_db.max().round(0), int(h[h.fc_hz==fc].tl_db.notna().sum()))","(float(np.round(np.nanmin(h[h.fc_hz==fc].tl_db),0)) if h[h.fc_hz==fc].tl_db.notna().any() else None, float(np.round(np.nanmax(h[h.fc_hz==fc].tl_db),0)) if h[h.fc_hz==fc].tl_db.notna().any() else None, int(h[h.fc_hz==fc].tl_db.notna().sum()))")
p.write_text(s)
EOF
python /tmp/note_numbers.py /tmp/tlg_tables_AB /tmp/tlg_ev_AB 2>&1 | sed -n 39,200p