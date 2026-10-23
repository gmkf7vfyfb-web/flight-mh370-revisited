cd rr/drive; python - <<'EOF'
L=open('sir.txt',encoding='utf-8',errors='ignore').read().split('\n')
idx=[i for i,x in enumerate(L) if x.startswith('--- page')]
for p in [49,50,52,64,328,361]:
    i=idx[p-1]; print(p,[x.strip() for x in L[i+1:i+5] if x.strip()][:3])
EOF