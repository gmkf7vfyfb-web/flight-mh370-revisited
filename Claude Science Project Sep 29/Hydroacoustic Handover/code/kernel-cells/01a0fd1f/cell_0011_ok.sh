cd rr
curl -sL -m 60 -o kane.pdf "https://casis.llnl.gov/content/pages/casis-2014/docs/poster/Kane1-CASIS-2014.pdf"; echo "kane $? $(wc -c < kane.pdf)"; file kane.pdf
for s in I06H1 I04H1 I07H1 I52H1; do for t in "2014-03-07T18:00:00&end=2014-03-07T18:10:00" "2014-04-05T00:00:00&end=2014-04-05T00:10:00"; do
code=$(curl -sL -m 120 -o ds.mseed -w "%{http_code} %{url_effective}" "https://service.iris.edu/fdsnws/dataselect/1/query?net=IM&sta=$s&cha=BDF&start=$t"); echo "$s $t -> $code $(wc -c < ds.mseed)"; done; done
curl -sL -m 60 "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=I04*,I07*,I52*&level=station&format=text" | head -30