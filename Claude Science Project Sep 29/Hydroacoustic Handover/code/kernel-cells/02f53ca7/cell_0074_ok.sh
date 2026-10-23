set -e; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
i=s.index('TIMESTAMP CORRECTION'); j=s.index('# IMPLEMENTATION is appended')
block=s[i:j]; s=s[:i]+s[j:]
# insert inside the docstring, before its closing quotes
k=s.index('"""\n# IMPLEMENTATION is appended')
s=s[:k]+block+s[k:]
open('tl_recal_block9.py','w').write(s); import ast; ast.parse(s); print('syntax ok')
print(s[k-200:k+len(block)+60])
EOF