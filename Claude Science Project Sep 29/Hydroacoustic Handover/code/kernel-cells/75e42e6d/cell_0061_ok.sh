cd src; python - <<'EOF'
import pymupdf
d=pymupdf.open('metron_af447.pdf'); print(len(d))
for i,p in enumerate(d):
    t=p.get_text()
    if 'Appendix B' in t or 'Table 4' in t or 'ULBs' in t and 'Crashes' in t:
        print('=== page',i+1); print(t[:3500])
EOF