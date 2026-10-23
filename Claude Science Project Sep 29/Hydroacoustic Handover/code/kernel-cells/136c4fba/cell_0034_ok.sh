cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
git checkout -- "$P/coordination" "$P/threads" 2>/dev/null; git status --porcelain | head
python3 -m py_compile "$P/engine/hypotheses/hydroacoustics/prepare/kadri_northern_conditional.py" && echo "compiles"
git add "$P/engine/hypotheses/hydroacoustics/prepare/kadri_northern_conditional.py"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics run J Task 1: PRE-REGISTRATION of the Kadri northern conditional (both times), committed before any statistic" && git log --oneline -1