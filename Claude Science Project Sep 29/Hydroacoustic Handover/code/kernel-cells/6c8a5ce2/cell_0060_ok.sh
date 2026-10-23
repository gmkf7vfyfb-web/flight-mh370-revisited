cd .tmp/standin; python - <<'EOF'
s=open("chart_tau.py").read()
s=s.replace('ax[2].set_title(f"C. Rows the non-detections penalise\\n(open: scenario prior; filled: water-entry model; {tag})")','ax[2].set_title(f"C. Rows the non-detections count against\\n({tag})")')
open("chart_tau.py","w").write(s)
EOF
grep -n "C. Rows" chart_tau.py