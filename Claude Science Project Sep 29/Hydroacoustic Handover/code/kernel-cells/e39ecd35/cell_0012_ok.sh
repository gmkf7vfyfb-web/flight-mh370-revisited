cd src
dl(){ code=$(curl -sS -m 240 -L -o "$2" -w "%{http_code} %{size_download}" "$1" 2>&1); echo "$code  $2"; }
dl "https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/acaps/777_2lr3er.pdf" boeing_acap_777_2lr3er.pdf
dl "https://www.atsb.gov.au/sites/default/files/media/5773567/mh370_ocean_driftiv_oct2017.pdf" csiro_drift_partIV_oct2017.pdf
dl "https://www.mh370-caption.net/wp-content/uploads/Blelly-Analysis-of-Flight-MH370.pdf" blelly_marchand_analysis.pdf
ls -la *.pdf