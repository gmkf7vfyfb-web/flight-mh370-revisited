cd "repo/Claude Science Project Sep 29"
n=$(grep -n "Refresh v2" threads/master-prompts/hydroacoustics.md | head -1 | cut -d: -f1); echo "start line $n"
sed -n "${n},625p" threads/master-prompts/hydroacoustics.md