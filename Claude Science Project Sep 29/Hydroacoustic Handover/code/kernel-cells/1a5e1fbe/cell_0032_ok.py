ia=pages('iannello.pdf'); print(len(ia))
txt=re.sub(r'\s+',' ',' '.join(ia))
k=txt.find('Comments') ; print(len(txt), k)
print(txt[:9000])