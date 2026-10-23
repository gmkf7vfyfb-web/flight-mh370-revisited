cd src
curl -sS --http1.1 -m 120 -D - -o /dev/null -r 0-1000 "https://www.atsb.gov.au/sites/default/files/media/5773567/mh370_ocean_driftiv_oct2017.pdf" 2>&1 | head -20
echo "=== second ==="
curl -sS --http1.1 -m 120 -D - -o /dev/null -r 0-1000 "https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" 2>&1 | head -20