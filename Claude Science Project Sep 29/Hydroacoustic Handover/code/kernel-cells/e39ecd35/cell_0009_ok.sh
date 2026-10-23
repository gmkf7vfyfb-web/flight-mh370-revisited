cd src
for u in \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/MH%20370%20Safety%20Investigation%20Report.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/Appendices.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/Appendix%201.6E.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/Safety%20Investigation%20Report.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/MH%20370%20Safety%20Investigation%20Report%20Slides.pdf" ; do
 code=$(curl -sS -m 90 -o /dev/null -L -w "%{http_code} %{size_download}" "$u" 2>&1)
 echo "$code  $u"
done