cd /Users/pete/Downloads 2>/dev/null && ls -d flight-mh370-revisited mh370-exchange mh370-inputs mh370-large-files 2>/dev/null
echo "--- filename matches"
find /Users/pete/Downloads -iname "*metz*" -o -iname "*airplane*crash*" -o -iname "*remote*hydroacoustic*" -o -iname "*pageoph*" -o -iname "*s00024*" 2>/dev/null | head
echo "--- all PDFs with hydro/f35/f-35 in name"
find /Users/pete/Downloads -iname "*.pdf" 2>/dev/null | grep -iE "hydro|f35|f-35|acoust" | head -30
echo "--- repo git grep"
cd /Users/pete/Downloads/flight-mh370-revisited 2>/dev/null && git ls-files | grep -iE "metz|airplane|pageoph|s00024" | head; git branch --show-current
echo "--- repo-wide ls-tree on all remote branches for pdf names"
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null); do git ls-tree -r --name-only $b 2>/dev/null | grep -iE "metz|airplane|pageoph|s00024|hydroacoustic.*\.pdf"; done | sort -u | head -20