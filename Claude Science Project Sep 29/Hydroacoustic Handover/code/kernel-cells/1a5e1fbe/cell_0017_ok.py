for i in range(8,min(13,len(c4))):
    print('==C4 PDF p',i+1); print(re.sub(r'\s+',' ',c4[i])[:3800])
print('########'); 
for i in [28,29]: print('==C1 PDF p',i+1); print(re.sub(r'\s+',' ',c1[i])[:2600])