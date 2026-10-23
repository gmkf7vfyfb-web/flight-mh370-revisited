mkdir -p audit/lit && cd audit/lit && curl -sS -L -o AD0734381.pdf https://apps.dtic.mil/sti/tr/pdf/AD0734381.pdf; ls -la AD0734381.pdf; file AD0734381.pdf; python3 -c "
import pypdfium2 as p; d=p.PdfDocument('AD0734381.pdf'); print(len(d)); 
t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
import re
for i,x in enumerate(t):
  if re.search(r'(?i)table|bubble period|time constant|energy flux',x): print(i+1, len(x), x[:200].replace('\n',' '))
" 2>&1 | head -40