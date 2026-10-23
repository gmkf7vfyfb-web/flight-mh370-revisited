cd "repo/Claude Science Project Sep 29"
echo "=== BRIEF size/headings"; wc -c threads/master-prompts/hydroacoustics.md; grep -n '^#' threads/master-prompts/hydroacoustics.md | head -80
echo "=== INBOX size"; wc -c coordination/HYDROACOUSTICS.md; grep -n '^#' coordination/HYDROACOUSTICS.md | tail -40
echo "=== git log touching hydro paths (work branch, shallow so limited)"; git log --oneline -- coordination/HYDROACOUSTICS.md threads/master-prompts/hydroacoustics.md | head
echo "=== architecture.md hydro mentions since 17 Oct"; grep -n -i 'hydro' coordination/architecture.md | tail -40