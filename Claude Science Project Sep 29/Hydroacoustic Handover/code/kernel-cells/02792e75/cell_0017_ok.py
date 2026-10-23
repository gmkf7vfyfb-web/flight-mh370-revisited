open("ctx2017.txt","w").write(t[79000:111000]); 
# also locate other things: 'white', '25°', 'Echo' contexts outside region
for kw in ["white","Tireless","submarine","25.975","sonobuoy"]:
    print(kw,[m.start() for m in re.finditer(kw,t)][:15])