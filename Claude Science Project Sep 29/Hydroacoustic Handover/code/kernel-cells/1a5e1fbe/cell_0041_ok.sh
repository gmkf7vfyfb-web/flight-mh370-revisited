cd pod; python3 -c "
import re;h=open('post.html',encoding='utf-8',errors='ignore').read();i=h.find('Steel');print(re.sub(r'\s+',' ',h[i-400:i+100]))"