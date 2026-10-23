cd src
curl -sS -m 120 -L -o mot_sir_slides.pdf "https://www.mot.gov.my/en/Laporan%20MH%20370/MH%20370%20Safety%20Investigation%20Report%20Slides.pdf" && ls -la mot_sir_slides.pdf
for u in \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/1.%20MH370%20-%20Safety%20Investigation%20Report.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/MH370%20Safety%20Investigation%20Report.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/Main%20Report.pdf" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/Appendix%201.6E%20Boeing%20Performance%20Analysis.pdf" \
 "https://www.mot.gov.my/en/aviation/mh370" \
 "https://www.mot.gov.my/en/Laporan%20MH%20370/" ; do
 code=$(curl -sS -m 90 -o /dev/null -L -w "%{http_code} %{size_download}" "$u" 2>&1); echo "$code  $u"
done