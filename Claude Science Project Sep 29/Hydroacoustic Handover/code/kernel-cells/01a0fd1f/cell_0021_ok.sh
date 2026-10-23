cd rr/drive; python - <<'EOF'
L=open('sir.txt',encoding='utf-8',errors='ignore').read().split('\n')
for a,b in [(2385,2450),(2700,2722),(2960,3036)]:
    print('#### lines',a); print('\n'.join(x for x in L[a:b] if x.strip()))
EOF