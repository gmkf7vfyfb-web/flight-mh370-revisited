cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
cat > commit.sh <<'E'
#!/bin/bash
# usage: commit.sh <clone> <branch> <message> <paths...>
set -e
CL=$1; B=$2; MSG=$3; shift 3
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd "$CL"
for try in 1 2 3; do
  git fetch -q --depth 1 "$URL" "$B:refs/remotes/origin/$B" 2>/dev/null || git fetch -q "$URL" "+$B:refs/remotes/origin/$B"
  export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
  git read-tree origin/$B
  git add --sparse "$@"
  TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l)
  [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
  C=$(git -c user.name="Hydroacoustic Module (metz-f35a)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "$MSG")
  if git push -q "$URL" $C:refs/heads/$B 2>/dev/null; then echo "PUSHED $C ($OLD -> $NEW files)"; unset GIT_INDEX_FILE; exit 0; fi
  echo "push rejected, retry $try"; sleep 3
done
exit 1
E
chmod +x commit.sh
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
du -sh "hydro/$P/results-data/digitised/metz2023" "hydro/$P/results-data/digitised/kadri-2019"
./commit.sh hydro hypothesis/hydroacoustics "hydroacoustics: digitise Metz et al. 2023 (F-35A at H11) and Kadri 2019; pre-register the F-35A anchor, real-arrival, route-2 and pulse checks (correction of G4/G5: both papers held)" "$P/prepare/digitise_metz_2023.py" "$P/prepare/digitise_kadri_2019.py" "$P/prepare/metz_f35a/prereg.py" "$P/results-data/digitised/MANIFEST.csv" "$P/results-data/digitised/metz2023" "$P/results-data/digitised/kadri-2019"