for s in ["next-free","next-repro-radar","next-routes"]:
    RS=recd(O/s)
    for k in RS:
        if not (s2m(RS[k]["window_start"])>=s2m(R289[k]["window_start"]) and s2m(RS[k]["window_end"])<=s2m(R289[k]["window_end"])):
            print(s,k,RS[k]["window_start"],RS[k]["window_end"],"| ref",R289[k]["window_start"],R289[k]["window_end"])