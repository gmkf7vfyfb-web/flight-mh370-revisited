cd src; curl -s -L --max-time 60 -w "\nHTTP %{http_code}\n" "https://data.mendeley.com/datasets/nr4vt4h8gt/1" -o mdl.html; ls -la mdl.html; python - <<'EOF'
import re,html
t=open('mdl.html',errors='ignore').read()
print(re.findall(r'"filename"\s*:\s*"([^"]+)"',t)[:50])
print(re.findall(r'"name"\s*:\s*"([^"]{3,120})"',t)[:60])
s=html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<script.*?</script>','',t,flags=re.S))); print(re.sub(r'\s+',' ',s)[:1500])
EOF