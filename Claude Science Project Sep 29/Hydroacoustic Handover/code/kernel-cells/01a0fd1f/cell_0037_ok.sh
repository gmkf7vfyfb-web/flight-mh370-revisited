cd rr; python - <<'EOF'
import re
t=open('mis2014.txt').read()
i=t.find('Tableau 3'); i=t.find('Tableau 3',i+50)
print(t[i-3000:i+400])
EOF