cd v5 && python3 - <<'E'
p='hydro-fix-proposal.md'; t=open(p).read()
t=t.replace('- The amplitude-aware likelihood.\n## 5a.','- The amplitude-aware likelihood.\n\n## 5a.')
open(p,'w').write(t)
import math; print(round(math.log10(1e-2/2.26e-3),3))
E
grep -n -E "^#|^[0-9]\. \*\*" hydro-fix-proposal.md | head -30