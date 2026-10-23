for name,txt in [("2017",a),("2014",b)]:
    for kw in ["Benthos","80 kHz","5 kHz","practical","4,500","4.5 km","1,730","sonobuoy","Tireless","submarine"]:
        for m in re.finditer(re.escape(kw),txt):
            print(name,kw,m.start(),C(txt[max(0,m.start()-250):m.start()+300]).replace("\n"," "))
            print("--")
        