cd src
curl -sS -m 240 -L -o poll_part1.pdf -w "%{http_code} %{size_download}\n" "https://elib.dlr.de/135592/1/Poll_Schumann_estimation_method_fuel_burn_performance_aircraft_cruise_part_1_fundamentals_2020.pdf"
file poll_part1.pdf
python3 -c "
import pypdfium2 as p, re
try:
    d=p.PdfDocument('poll_part1.pdf')
    t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
    for i,x in enumerate(t):
        for ln in x.split('\n'):
            if re.search(r'777', ln): print(i+1,'|',ln.strip()[:160])
except Exception as e: print('ERR',e)
" | head -25