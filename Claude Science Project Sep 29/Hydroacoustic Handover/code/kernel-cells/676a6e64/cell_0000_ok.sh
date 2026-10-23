set -e
cd "$PWD"
if [ ! -d repo ]; then
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited" repo
fi
cd repo
git sparse-checkout set "Claude Science Project Sep 29" 2>/dev/null
git log -1 --format='%h %ad %s' --date=short
echo "--- remote branches"
git ls-remote --heads origin | awk '{print $2}' 
echo "--- hydro branch head"
git ls-remote origin refs/heads/hypothesis/hydroacoustics
cd "Claude Science Project Sep 29"
echo "--- top-level"
ls
echo "--- hydro-related files"
find . -iname '*hydro*' -o -iname '*kadri*' -o -iname '*acoustic*' | sort
echo "--- threads tree"
find threads -maxdepth 2 | sort
ls coordination 2>/dev/null