cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "status" hypothesis.toml | head -10; echo "---"; sed -n 1,30p hypothesis.toml