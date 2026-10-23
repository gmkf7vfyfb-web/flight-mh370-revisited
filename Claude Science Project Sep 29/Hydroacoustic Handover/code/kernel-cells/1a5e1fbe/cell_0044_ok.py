P=pages('griffin_web.pdf'); T=re.sub(r'\s+',' ',' '.join(P)); print(T[:3500])
k=T.find('short report'); print('....',T[k-600:k+1200])