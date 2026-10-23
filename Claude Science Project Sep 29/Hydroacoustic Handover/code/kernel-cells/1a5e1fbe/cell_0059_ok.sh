python3 - <<'E'
p='research-surface-search-pod.md'; s=open(p).read()
s=s.replace("Metron's 2011 report for the BEA (section 4.2, PDF pp.16-20)","Metron's 2011 report for the BEA (section 4.2, printed pp.12-17)")
s=s.replace("Metron 2011 (PDF pp.20-21) equivalently","Metron 2011 (printed pp.17-18) equivalently")
open(p,'w').write(s); print(s.count('printed pp.12-17'), s.count('printed pp.17-18'))
E