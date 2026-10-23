cd leg; python - <<'E'
s=open('blockage.py').read()
s=s.replace('BLOCKED: any land, or > 10 km shallower than 200 m;','BLOCKED: any land, or > 10 km shallower than 200 m, or > 100 km shallower than 1,000 m (long shelf; added after the first\npass so that Scott Reef agrees with the module GEBCO authority of 9 Oct, disclosed);')
s=s.replace('cls = "BLOCKED" if (land > 0 or sh200 > 10)','cls = "BLOCKED" if (land > 0 or sh200 > 10 or sh1000 > 100)')
open('blockage.py','w').write(s)
E
python blockage.py out/path_blockage.csv 2>&1 | grep -v -i proj | head -17