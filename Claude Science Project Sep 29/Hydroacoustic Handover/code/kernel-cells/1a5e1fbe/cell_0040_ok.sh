cd pod; python3 - <<'E'
import re
h=open('post.html',encoding='utf-8',errors='ignore').read()
i=h.find('Obtaining the Images'); seg=h[i:i+4000]
for m in re.finditer(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',seg): print(m.group(2)[:60],'->',m.group(1))
E