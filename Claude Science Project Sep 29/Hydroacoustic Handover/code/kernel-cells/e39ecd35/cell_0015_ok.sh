cd src
dl(){ code=$(curl -sS -m 180 -L -o "$2" -w "%{http_code} %{size_download}" "$1" 2>&1); echo "$code  $2  <- $1"; }
dl "https://www.easa.europa.eu/sites/default/files/dfu/TCDS_EASA.IM.A.003_B777_Iss21.pdf" easa_tcds_777.pdf
dl "https://drs.faa.gov/browse/excelExternalWindow/DRSDOCID116696445620250218194058.0001?modalOpened=true" faa_tcds_777.pdf
head -c 200 easa_tcds_777.pdf | file - ; ls -la easa_tcds_777.pdf faa_tcds_777.pdf 2>/dev/null