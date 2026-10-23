j=a.find('13- Apr- 14'); print(re.sub(r'\s+',' ',a[j:j+1500]))
j=a.find('**Table 18:'); k=a.find('Surface search coverage and confidence**')
seg=re.sub(r'\s+',' ',a[j:k]); m=seg.find('18-Apr'); print(seg[m-50:])