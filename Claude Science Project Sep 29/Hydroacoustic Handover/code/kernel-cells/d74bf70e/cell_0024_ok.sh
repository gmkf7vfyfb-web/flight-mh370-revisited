cd hydro
curl -s -m 90 -o im_channels_2014.txt "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=H01W*,H08N*,H08S*,H11N*,H11S*,H03N*,H03S*,H04N*,H04S*,H10N*,H10S*&level=channel&format=text&starttime=2014-03-07&endtime=2014-03-09"; echo rc=$?
curl -s -m 90 -o im_channels_all.txt "https://service.iris.edu/fdsnws/station/1/query?net=IM&sta=H*&level=channel&format=text"; echo rc=$?
wc -l im_channels_2014.txt im_channels_all.txt; head -4 im_channels_2014.txt; cut -d'|' -f2 im_channels_all.txt | sort -u | tr '\n' ' '