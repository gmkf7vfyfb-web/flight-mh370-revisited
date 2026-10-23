cd hydro
curl -s -m 90 -w '\nHTTP %{http_code}\n' "https://service.iris.edu/fdsnws/station/1/query?net=IM&level=station&format=text" -o im_sta.txt; tail -1 im_sta.txt; wc -l im_sta.txt
grep -E '\|H[0-9]' im_sta.txt | head -30
curl -s -m 60 -w 'HTTP %{http_code}\n' -o /dev/null "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=H01W1&level=channel&format=text"