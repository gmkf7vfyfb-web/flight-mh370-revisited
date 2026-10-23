
top=[(os.path.basename(p),sz) for p,sz in pdfs if os.path.dirname(p)=='/Users/pete/Downloads']
top.sort()
print(len(top))
print(' | '.join(f"{n[:58]}" for n,_ in top))
