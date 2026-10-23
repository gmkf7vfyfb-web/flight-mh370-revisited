import hashlib, os
p = host.artifact_path("5821ab6a-dfc9-453f-9cb0-94614a3f6c45"); b=open(p,'rb').read()
print(len(b), hashlib.sha256(b).hexdigest())