mkdir -p hydro && cd hydro
curl -s -m 60 -o im_stations_channel.txt "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=H01W*,H08N*,H08S*,H11N*,H11S*,H03N*,H03S*,H04N*,H04S*,H10N*,H10S*&level=channel&format=text&starttime=2014-03-07&endtime=2014-03-09" ; echo rc=$?
wc -l im_stations_channel.txt; head -c 300 im_stations_channel.txt