cd rr
curl -sL -m 300 -o sir.pdf -w "%{http_code} %{url_effective}\n" "http://mh370.mot.gov.my/MH370SafetyInvestigationReport.pdf"; ls -la sir.pdf; file sir.pdf