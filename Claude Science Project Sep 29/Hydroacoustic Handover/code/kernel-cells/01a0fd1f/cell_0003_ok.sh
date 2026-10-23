mkdir -p rr && cd rr
curl -sL -m 60 -o ctbto.pdf "https://www.ctbto.org/sites/default/files/Documents/IDC_infrasound_MalaysianAirlines_MH370.pdf"; echo "ctbto $? $(wc -c < ctbto.pdf)"
curl -sL -m 60 -o wise_radar.html "http://www.jeffwise.net/2014/11/18/mh370-and-the-mystery-of-indonesian-radar/"; echo "wise $? $(wc -c < wise_radar.html)"
curl -sL -m 60 -o cocos370.html "https://370location.org/2018/08/cocos-island-infrasound-may-be-key-to-locating-mh370/"; echo "370 $? $(wc -c < cocos370.html)"
file ctbto.pdf