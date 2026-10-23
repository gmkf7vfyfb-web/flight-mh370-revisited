
import re, html as H
def totext(p):
    s=open(p,encoding="utf8",errors="ignore").read()
    s=re.sub(r"(?is)<(script|style).*?</\1>"," ",s)
    s=re.sub(r"(?s)<[^>]+>"," ",s)
    return re.sub(r"[ \t]+"," ", H.unescape(s))
eof = totext("src/rp_eof.html"); bank = totext("src/rp_banked.html")
open("src/rp_eof.txt","w").write(eof); open("src/rp_banked.txt","w").write(bank)
i = eof.find("End-of-Flight Simulations of MH370")
print(len(eof), i)
print(eof[i:i+7000])
