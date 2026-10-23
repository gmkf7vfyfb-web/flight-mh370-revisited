cd ./.tmp; curl -s -m 30 -o duncan.html -w "%{http_code}\n" "https://acoustics.org/the-loss-of-an-f35-fighter-aircraft-and-the-search-for-malaysian-airlines-flight-mh370/"; python3 -c "
import re,html
t=open('duncan.html',encoding='utf8',errors='ignore').read()
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
s=html.unescape(re.sub(r'<[^>]+>','\n',t)); s=re.sub(r'\n\s*\n+','\n',s)
i=s.find('Centre for Marine Science'); print(s[i:i+6500])
"