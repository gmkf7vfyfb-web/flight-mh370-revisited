cd src
probe(){ echo "-- $2 $1"; curl -sS $2 -m 60 -o /dev/null -L -w "   code=%{http_code} size=%{size_download} t=%{time_total}\n" "$1" 2>&1 | tail -2; }
probe "https://www.atsb.gov.au/" "--http1.1"
probe "https://www.atsb.gov.au/" ""
probe "https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" "--http1.1"
probe "https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" "--http1.1 -r 0-200000"