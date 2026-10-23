cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; grep -n "^def \|^    def " tl_recal_block9.py ram_tl_check.py imos_ram_grid.py | head -40; python - <<'EOF'
t=open('tl_recal_block9.py').read(); i=t.find('def ram_job'); print(t[i:i+3500])
EOF