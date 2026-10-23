cd hydro
B="https://service.earthscope.org/fdsnws/station/1/query"
curl -s -m 90 -o im_sta.txt "$B?net=IM&level=station&format=text"; wc -l im_sta.txt
grep -E '^IM\|H' im_sta.txt | head -40
curl -s -m 120 -o im_hyd_channels.txt "$B?net=IM&sta=H*&level=channel&format=text"; wc -l im_hyd_channels.txt; head -3 im_hyd_channels.txt