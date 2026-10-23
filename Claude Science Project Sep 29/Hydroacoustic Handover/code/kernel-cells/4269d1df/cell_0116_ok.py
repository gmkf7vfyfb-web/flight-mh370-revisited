import re
s=open('out/README.md').read()
s=re.sub(r'\]\(\{/Users/[^)]*?/v[0-9a-f]{8}_(fig-[a-z0-9-]+\.png)\}\)', r'](\1)', s)
print([l for l in s.splitlines() if 'fig-' in l and '](' in l])
assert '/Users/' not in s
open('out/README.md','w').write(s)
