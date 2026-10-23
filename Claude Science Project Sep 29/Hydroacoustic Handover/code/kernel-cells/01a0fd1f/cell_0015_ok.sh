cd /Users/pete/Downloads; find . -maxdepth 6 \( -iname "*safety*invest*" -o -iname "*SIR*" -o -iname "*underwater*search*" -o -iname "*AE-2014-054*" -o -iname "*ae2014054*" \) 2>/dev/null | head -20
cd ~/; cd - >/dev/null
cd "$OLDPWD" 2>/dev/null
mkdir -p /tmp/x; cd /tmp/x
for u in "http://mh370.mot.gov.my/MH370SafetyInvestigationReport.pdf" "https://www.mot.gov.my/en/Laporan%20MH%20370/MH370SafetyInvestigationReport.pdf"; do curl -sL -m 60 -o sir.pdf -w "%{http_code} " "$u"; echo "$? $(wc -c < sir.pdf 2>/dev/null) $u"; done