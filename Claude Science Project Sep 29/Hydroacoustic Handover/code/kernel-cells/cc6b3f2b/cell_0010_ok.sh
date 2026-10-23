cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -c . 
git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep "^Archive" | head -3
git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "figure9" | head
echo "--- try other branches"
git ls-remote --heads origin 2>/dev/null | awk '{print $2}' | head -30
echo "--- disk search"
ls /Users/pete/Downloads/ | head -40
find /Users/pete/Downloads -maxdepth 4 -iname "*figure9*" 2>/dev/null | head