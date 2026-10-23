cd rr/drive; python - <<'EOF'
import re
L=open('sir.txt',encoding='utf-8',errors='ignore').read().split('\n')
for n in [2398,2545,3014,14111,15620]:
    for j in range(n,-1,-1):
        if L[j].startswith('--- page'):
            print(n,L[j], '| next lines:', [x.strip() for x in L[j+1:j+4]]); break
EOF