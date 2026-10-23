cd src
dl(){ code=$(curl -sS -m 240 -L -o "$2" -w "%{http_code} %{size_download}" "$1" 2>&1); echo "$code  $2"; file "$2"; }
dl "https://www.easa.europa.eu/en/downloads/7521/en" easa_tcds_777.pdf
dl "https://www.aviation.govt.nz/assets/aircraft/type-acceptance-reports/Boeing-777.pdf" nzcaa_tar_777.pdf