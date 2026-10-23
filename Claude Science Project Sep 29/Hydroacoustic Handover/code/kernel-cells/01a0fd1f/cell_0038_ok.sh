cd rr; python - <<'EOF'
t=open('mis2015.txt').read()
i=t.find('Tableau 1 :'); i=t.find('Tableau 1 :',i+50)
print(t[i-200:i+2600])
import re
for m in re.finditer(r'NE-?AMS',t):
    pass
j=t.find('hélice'); print('---hélice', t[j-1500:j+500] if j>0 else 'none')
EOF