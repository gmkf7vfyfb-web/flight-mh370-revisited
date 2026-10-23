cd rr
curl -sL -m 180 -o ucrl.pdf "https://www.osti.gov/servlets/purl/850576"; echo "ucrl $? $(wc -c < ucrl.pdf)"; file ucrl.pdf
curl -sL -m 180 -o stead.pdf "https://www.osti.gov/servlets/purl/1136454"; echo "stead $? $(wc -c < stead.pdf)"; file stead.pdf