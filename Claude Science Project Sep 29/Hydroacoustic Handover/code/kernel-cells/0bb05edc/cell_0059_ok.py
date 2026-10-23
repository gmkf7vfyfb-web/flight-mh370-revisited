
r = host.mcp("google-drive","read_file_content", fileId="1nHzJ3h-IcsCkTzvTJwYK0V7-A20F-BHE")
t = r.get('fileContent','')
print(r.get('title'), len(t))
print(t[:900].replace('\n',' '))
