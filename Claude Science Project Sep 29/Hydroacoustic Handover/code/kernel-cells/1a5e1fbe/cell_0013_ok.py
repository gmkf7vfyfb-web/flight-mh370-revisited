for i in [43,44]:
    print('=====PDF p',i+1); print(re.sub(r'\n\s*\n','\n',d2[i].get_text())[:5000])