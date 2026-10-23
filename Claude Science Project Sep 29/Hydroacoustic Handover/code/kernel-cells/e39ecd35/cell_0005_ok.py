
blocks = {b.split("===")[0].strip(): b.split("===",1)[1] for b in ht.split("===PAGE ")[1:]}
out = "".join(blocks[k] for k in ["8","9","10"])
open("src/holland_tail.txt","w").write(out)
print(len(out))
