k=('silent','H08S','agw'); print(RM[k]["window_start"],RM[k]["window_end"],R289[k]["window_start"],R289[k]["window_end"])
RS=recd(O/"next-routes"); k=('silent','3250','sofar'); print(RS[k]["window_start"],RS[k]["window_end"],R289[k]["window_start"])
RS=recd(O/"next-free"); 
for k in [('alive','H08S','agw'),('alive','3274','agw')]: print(k,RS[k]["window_start"],RS[k]["window_end"],R289[k]["window_start"],R289[k]["window_end"])