
import requests, pypdf, io, hashlib, os
urls = {
 'Hao_2024_Spaceborne_SAR_aerial_moving_target_RemoteSensing16-2392.pdf':'https://www.mdpi.com/2072-4292/16/13/2392/pdf',
 'Remote_Sensing_2025_17-2918_Air_moving-target_detection_sub-aperture_GoDec.pdf':'https://www.mdpi.com/2072-4292/17/16/2918/pdf',
}
for fn,u in urls.items():
    try:
        r=requests.get(u, timeout=60, allow_redirects=True)
        ok = r.status_code==200 and r.content[:4]==b'%PDF'
        print(fn[:50], r.status_code, r.headers.get('content-type','')[:30], len(r.content), 'PDF' if ok else r.content[:80])
        if ok:
            open(fn,'wb').write(r.content)
            pr=pypdf.PdfReader(io.BytesIO(r.content)); print('   ',len(pr.pages),'pp |',(pr.pages[0].extract_text() or '')[:140].replace('\n',' '))
    except Exception as e:
        print(fn[:50],'ERR',str(e)[:150])
