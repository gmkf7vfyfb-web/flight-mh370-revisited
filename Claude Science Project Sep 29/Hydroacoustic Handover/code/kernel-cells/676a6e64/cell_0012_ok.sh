cd repo
echo "=== kadri files anywhere on module branch"; git ls-tree -r FETCH_HEAD --name-only | grep -i -E 'kadri|royer|ohasisbio' | grep -v -E '\.(png|pdf)$'
cd "Claude Science Project Sep 29"
echo; echo "=== table1 test A + establishes"; sed -n '19,41p;73,94p' results/hydroacoustics-kadri-table1-test.md | cut -c1-330
echo; echo "=== EW0112 note head"; sed -n '1,40p' results/hydroacoustics-air9-ew0112-source-reference.md | cut -c1-330