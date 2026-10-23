cd src
for u in \
 "https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/acaps/777_23.pdf" \
 "https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/acaps/777-200_300.pdf" \
 "https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/acaps/777_2-3.pdf" \
 "https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/acaps/777.pdf" ; do
 code=$(curl -sS -m 120 -o /dev/null -L -w "%{http_code} %{size_download}" "$u" 2>&1); echo "$code  $u"
done