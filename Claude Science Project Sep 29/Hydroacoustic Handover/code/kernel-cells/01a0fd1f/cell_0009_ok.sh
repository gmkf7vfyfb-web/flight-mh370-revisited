cd rr
curl -sL -m 60 -o kane.pdf "https://casis.llnl.gov/content/pages/casis-2014/docs/poster/Kane1-CASIS-2014.pdf"; echo "kane $? $(wc -c < kane.pdf)"; head -c 300 kane.pdf | strings | head -3
curl -sL -m 60 "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=I06*&level=station&format=text" | head -20
echo ---
curl -sL -m 60 "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=I06H1&level=channel&format=text" | head -20
echo --- avail
curl -sL -m 60 "https://service.iris.edu/fdsnws/availability/1/extent?net=IM&sta=I06H1&format=text" | head