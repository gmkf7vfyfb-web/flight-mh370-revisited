cd repo && F="Claude Science Project Sep 29/coordination/architecture.md"
sed -n 1036,1040p "$F" | cut -c1-120
git add "$F" && GIT_EDITOR=true git rebase --continue >/dev/null && timeout 60 git push -q origin HEAD:claude-science-sep29 && git log --oneline -2 && git ls-remote origin claude-science-sep29