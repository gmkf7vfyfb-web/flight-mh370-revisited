cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
git reset -q --soft HEAD~1 && git reset -q
git add "$P/coordination" "$P/threads"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics: sync coordination/ and threads/ to origin/claude-science-sep29 (housekeeping, no module content)"
git add "$P/engine/hypotheses/hydroacoustics/prepare/kadri_northern_conditional.py"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics run J Task 1: PRE-REGISTRATION of the Kadri northern conditional (both Kadri times), committed before any statistic"
git log --oneline -3; echo "--- tip stat ---"; git show --stat --oneline HEAD | tail -3; echo "--- clean? ---"; git status --porcelain | head