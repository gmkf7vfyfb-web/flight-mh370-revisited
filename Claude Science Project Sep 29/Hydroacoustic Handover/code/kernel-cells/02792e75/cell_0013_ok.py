r=host.mcp(S,"read_file_content",fileId="1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4")
t=r.get("fileContent","") if isinstance(r,dict) else str(r)
open("src/atsb2017_text.txt","w").write(t); print(len(t)); 
import re
for m in re.finditer(r"Haixun",t): pass
print(len(re.findall("Haixun",t)), len(re.findall("white object",t,re.I)))