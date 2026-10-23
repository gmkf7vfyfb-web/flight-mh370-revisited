echo TMP=$TMPDIR; ls -d $TMPDIR/repo ./repo 2>&1
cd $TMPDIR/repo 2>/dev/null || cd repo
git ls-tree -r --name-only HEAD | grep -i "coordination/" | head -20
cat >> .git/info/sparse-checkout <<'EOF'
/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/*.csv
/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/*.json
/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/*.py
/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/*.pdf
EOF
git ls-tree -r --name-only HEAD | grep "kadri-2024-hydroacoustics" | grep -v "\.md$" | wc -l
git ls-tree -r --name-only HEAD | grep -i "hydroacoust" | grep -v "kadri-2024-hydroacoustics" | grep -v "^ISO Sept 28 Status/results/worktree-hydro\|inputs/papers/hydro" | head -40