cd src
curl -sS -m 600 -L -o apo_page.html -w "page %{http_code} %{size_download}\n" "https://apo.org.au/node/112656"
grep -oE 'https?://[^"]*\.pdf' apo_page.html | sort -u | head -20
curl -sS -m 1800 -L -o atsb_operational_search_2017.pdf -w "pdf %{http_code} %{size_download}\n" "https://apo.org.au/sites/default/files/resource-files/2017-10/apo-nid112656.pdf"
file atsb_operational_search_2017.pdf; ls -la atsb_operational_search_2017.pdf