cd src
curl -sS -m 300 -L -o rp_2020.html -w "1 %{http_code} %{size_download}\n" "https://mh370.radiantphysics.com/2020/02/01/search-recommendation-for-mh370s-debris-field/"
grep -oE 'href="[^"]+\.pdf"' rp_2020.html | sort -u | head -20
curl -sS -m 300 -L -o rp_papers.html -w "2 %{http_code} %{size_download}\n" "https://mh370.radiantphysics.com/papers/"
grep -oE 'href="[^"]+\.pdf"' rp_papers.html | sort -u | head -40