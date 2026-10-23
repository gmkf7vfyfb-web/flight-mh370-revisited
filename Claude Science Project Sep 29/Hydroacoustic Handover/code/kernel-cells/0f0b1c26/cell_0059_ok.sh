cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
for f in ['../src/pmc24/41598_2024_60529_Fig8_HTML.jpg','../src/pmc24/41598_2024_60529_Fig5_HTML.jpg','../src/pmc24/41598_2024_60529_Fig7_HTML.jpg']:
    a=load(f); H,W,_=a.shape; print(f,W,H)
    print(' vlines',vlines(a,0,H,frac=0.12)[:24])
    print(' hlines',hlines(a,0,W,frac=0.12)[:40])
EOF