c=host.credentials.get("COPERNICUS")
v=c.get('value','')
print([k for k in c.keys()], c.get('provider'), c.get('credential_type'), len(v), ':' in v, v.strip().startswith('{'), '\n' in v.strip())