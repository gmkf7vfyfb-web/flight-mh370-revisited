cd src
dl(){ code=$(curl -sS --http1.1 -m 900 --retry 2 -L -o "$2" -w "%{http_code} %{size_download}" "$1" 2>&1); echo "$code  $2"; }
dl "https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" atsb_operational_search_2017.pdf
file atsb_operational_search_2017.pdf; ls -la atsb_operational_search_2017.pdf