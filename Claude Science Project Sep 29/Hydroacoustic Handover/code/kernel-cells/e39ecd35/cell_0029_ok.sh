cd src
curl -sS -m 300 -L -o apo_page.html -w "%{http_code} %{size_download}\n" "https://apo.org.au/node/112656"
grep -oE 'https?://[^"]*\.pdf' apo_page.html | sort -u | head -20