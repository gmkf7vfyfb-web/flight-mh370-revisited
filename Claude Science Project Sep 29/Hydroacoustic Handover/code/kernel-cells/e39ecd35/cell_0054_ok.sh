cd src
dl(){ echo "-- $2"; curl -sS -m 300 -L -o "$2" -w "   code=%{http_code} size=%{size_download}\n" "$1" 2>&1|tail -1; file "$2" 2>/dev/null; }
dl "https://publications.csiro.au/rpr/download?pid=csiro:EP167888&dsid=DS2" csiro_EP167888.pdf
dl "https://publications.csiro.au/rpr/download?pid=csiro:EP172633&dsid=DS2" csiro_EP172633.pdf