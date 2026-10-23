cd src
probe(){ echo "-- $1"; curl -sS --http1.1 -m 45 -o /dev/null -L -w "   code=%{http_code} size=%{size_download}\n" "$1" 2>&1 | tail -1; }
probe "https://atsb.gov.au/"
probe "https://www.mot.gov.my/en/Laporan%20MH%20370/MH370%20Safety%20Investigation%20Report%20-%20Main%20Report.pdf"
probe "https://www.mot.gov.my/en/Laporan%20MH%20370/Appendices%201.pdf"
probe "https://www.mot.gov.my/en/"