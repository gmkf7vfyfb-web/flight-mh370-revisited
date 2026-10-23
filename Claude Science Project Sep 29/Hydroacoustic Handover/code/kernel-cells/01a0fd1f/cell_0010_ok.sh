cd rr
for t in "2014-03-07T18:00:00&end=2014-03-07T18:10:00" "2014-04-05T00:00:00&end=2014-04-05T00:10:00" "2014-03-08T00:00:00&end=2014-03-08T00:10:00"; do
code=$(curl -s -m 90 -o ds.mseed -w "%{http_code}" "https://service.iris.edu/fdsnws/dataselect/1/query?net=IM&sta=I06H1&cha=BDF&start=$t"); echo "$t -> $code $(wc -c < ds.mseed)"; done
for s in I04H1 I07H1 I52H1; do curl -s -m 60 "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=$s&level=station&format=text" | tail -n +2; done
for s in I04H1 I52H1 I07H1; do code=$(curl -s -m 90 -o ds2.mseed -w "%{http_code}" "https://service.iris.edu/fdsnws/dataselect/1/query?net=IM&sta=$s&cha=BDF&start=2014-03-08T00:00:00&end=2014-03-08T00:10:00"); echo "$s 2014-03-08 -> $code $(wc -c < ds2.mseed)"; done