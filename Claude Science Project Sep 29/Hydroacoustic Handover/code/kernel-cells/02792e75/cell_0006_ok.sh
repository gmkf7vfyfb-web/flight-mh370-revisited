mkdir -p src; cd src
curl -sS -L -o atsb2017.pdf -w "%{http_code} %{size_download}\n" "https://www.atsb.gov.au/sites/default/files/2022-12/AE-2014-054_MH370-Search%20and%20debris%20examination%20update.pdf" --max-time 60 2>&1 | tail -1
curl -sS -I "https://www.atsb.gov.au/mh370-pages/updates/reports" --max-time 30 2>&1 | head -3