cd rr; curl -sL -m 60 -o atfm.pdf "https://us-indiaacp.com/downloads/seminars/atfm/ATFM_ACP.pdf"; echo "$? $(wc -c < atfm.pdf 2>/dev/null)"; python - <<'EOF' 2>/dev/null
import pypdf
r=pypdf.PdfReader('atfm.pdf'); print(len(r.pages), r.metadata)
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    if 'Port Blair' in t or 'PORT BLAIR' in t: print('=== PAGE',i+1); print(t[:1500])
EOF