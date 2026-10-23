cd fix-metz; P='Claude Science Project Sep 29'; sed -n '327,336p' "$P/paper/CITATIONS-LEDGER.md" | cut -c1-260; grep -n "Metz" "$P/paper/CITATIONS-LEDGER.md" | cut -c1-120
cd ..; python - <<'EOF'
import pypdf,re
r=pypdf.PdfReader('Metz_Obana_Fukao_2023_Remote_hydroacoustic_detection_airplane_crash.pdf')
txt="\n".join(p.extract_text() for p in r.pages)
for m in re.finditer(r'(Figure \d+\s*\n?.{0,260})', txt): print(m.group(1).replace("\n"," ")[:260]); print()
print('Table' in txt, len(txt))
for kw in ['Pa','spectrogram','band','Hz']:
    i=[m.start() for m in re.finditer(kw,txt)][:3]; print(kw, len(re.findall(kw,txt)))
EOF