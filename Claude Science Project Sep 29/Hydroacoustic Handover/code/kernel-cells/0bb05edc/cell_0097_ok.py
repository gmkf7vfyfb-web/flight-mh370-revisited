
def sha(b): return hashlib.sha256(b).hexdigest()
req_md=open(os.path.join(X,'REQUESTS.md'),'rb').read()
print('old md sha == old manifest hash:', sha(req_md)=='b5712a95fc2f29b81ea176b5ef7d7aa87191544a2588a483951c718c1c678e9c')
s=req_md.decode('utf-8')
new_s=s.replace("(Metz, Obana & Fukao 2023; the paper is closed access to us — gap G4)","(Metz, Obana & Fukao 2023; we hold the paper, so only the waveform is requested — gap G4)")
new_s=new_s.replace("(his own 2019 paper is\n   closed to us — gap G5)","(Dall'Osto 2019, JASA, treats this event; we hold no copy — gap G5)")
assert new_s!=s and new_s.count('closed')==s.count('closed')-2
new_md=new_s.encode('utf-8')
print('new md bytes == new module REQUESTS.txt bytes:', new_md==newb)
sums=open(os.path.join(X,'SHA256SUMS')).read()
print('SHA256SUMS lists REQUESTS.md:', 'REQUESTS' in sums)
