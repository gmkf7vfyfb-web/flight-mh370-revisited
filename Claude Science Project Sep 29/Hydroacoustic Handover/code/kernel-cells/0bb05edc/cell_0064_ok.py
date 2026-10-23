
import requests
tests = {
 'calhoun.nps.edu search': 'https://calhoun.nps.edu/discover?query=Prediction+of+falling+cylinder+through+air-water-sediment+columns',
 'museum.wa.gov.au': 'https://museum.wa.gov.au/maritime-archaeology-db/',
 'dnv.com RP-F107': 'https://www.dnv.com/oilgas/download/dnv-rp-f107-risk-assessment-of-pipeline-protection/',
 'knkt.go.id': 'https://knkt.go.id/',
}
for n,u in tests.items():
    try:
        r=requests.get(u, timeout=30)
        print(n, r.status_code, r.headers.get('content-type','')[:25], len(r.content), r.text[:70].replace('\n',' ') if r.status_code!=200 else '')
    except Exception as e:
        print(n,'ERR',str(e)[:120])
