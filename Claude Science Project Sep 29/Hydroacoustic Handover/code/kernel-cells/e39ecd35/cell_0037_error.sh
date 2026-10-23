cd src
sleep 20
for u in "https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf" ; do
  echo "try1: $(curl -sS -m 600 -L -o atsb_op.pdf -w '%{http_code} %{size_download} %{time_total}' "$u" 2>&1)"
done
file atsb_op.pdf 2>/dev/null; ls -la atsb_op.pdf 2>/dev/null