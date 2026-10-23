i=a.find('Table 12'); 
for t in ['Table 10:','Table 12:','Table 14:','Table 16:','Table 17:','Table 18:']:
    j=a.find('**'+t) if a.find('**'+t)>=0 else a.find(t)
    print('#####',t,'p',pgp(j)); print(re.sub(r'\s+',' ',a[j:j+1800]))