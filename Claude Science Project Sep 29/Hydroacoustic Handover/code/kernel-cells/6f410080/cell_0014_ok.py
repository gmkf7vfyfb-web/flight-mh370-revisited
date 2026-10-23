for f in txt:
    if 'handout' in f or '_tv' in f: print('#####',f,'|',re.sub(r'\s+',' ',txt[f]))