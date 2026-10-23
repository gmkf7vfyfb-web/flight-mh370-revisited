R="repo/Claude Science Project Sep 29/results"
sed -n '1,60p;123,235p' "$R/hydroacoustics-tl-grid-run-j.md" > /tmp/tl_excerpt.md; wc -c /tmp/tl_excerpt.md