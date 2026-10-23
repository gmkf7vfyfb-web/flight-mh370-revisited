cd src
curl -sS -m 180 -L -o rp_eof.html -w "1 %{http_code} %{size_download}\n" "https://mh370.radiantphysics.com/2018/08/19/end-of-flight-simulations-of-mh370/"
curl -sS -m 180 -L -o rp_banked.html -w "2 %{http_code} %{size_download}\n" "https://mh370.radiantphysics.com/2017/06/04/mh370-end-of-flight-with-banked-descent-and-no-pilot/"
grep -oE 'href="https?://[^"]+\.pdf"' rp_eof.html rp_banked.html | sort -u | head -30