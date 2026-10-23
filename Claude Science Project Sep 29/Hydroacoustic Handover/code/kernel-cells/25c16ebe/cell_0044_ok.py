v4 = open("audit/end-of-flight.md").read()
def show(anchor, n=420):
    i = v4.find(anchor); print(f"[{i}] >>>", repr(v4[i:i+n]), "\n")
show("## 1. Mission")
show("The module exists to produce")
show("6. **Measure ESS")
show("Two further hooks exist")
show("## 3. Build status")
show("| The EoF **model**")
