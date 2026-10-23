cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
git add --sparse -A . 2>&1 | grep -v "ignore\|failed to store" || true
git status --short | cut -c1-140
echo; git diff --cached --stat | tail -n 22
echo; echo "== sanity: any staged binary / big / sensitive files?"; git diff --cached --name-only | grep -i -E "\.(bin|xlsm|xls|xlsx|json)$|fuel-tables|tmp/" || echo none
echo "== residual blocking words in the edited text files (excluding the ledger/rulings):"
git diff --cached -U0 | grep '^+' | grep -v '^+++' | grep -i -E "closed access|paywall|not held|unobtainable" | cut -c1-200 | head