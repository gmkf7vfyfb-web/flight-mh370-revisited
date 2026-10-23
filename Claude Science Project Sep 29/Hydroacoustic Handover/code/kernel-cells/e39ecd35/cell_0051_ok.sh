cd src
for p in \
 "https://webarchive.nla.gov.au/awa/20180101000000/https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" \
 "https://webarchive.nla.gov.au/awa/20170101000000/https://www.atsb.gov.au/media/5771939/ae-2014-054_mh370-search-and-debris-update_2nov-2016_v2.pdf" ; do
 echo "-- $p"; curl -sS -m 300 -L -o tmp.bin -w "   code=%{http_code} size=%{size_download}\n" "$p" 2>&1 | tail -2; file tmp.bin
done