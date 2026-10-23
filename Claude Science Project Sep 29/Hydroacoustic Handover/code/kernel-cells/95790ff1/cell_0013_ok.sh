cd "repo/ISO Sept 28 Status/inputs/papers/hydroacoustics"; python3 -c "
import pypdfium2 as p; d=p.PdfDocument('ucrl-tr-207323.pdf'); print(len(d)); 
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range(); print(i+1, len(t), repr(t[:80]))
" 2>&1 | head -80; head -c 1500 ucrl-tr-207323.txt; grep -n -c . ucrl-tr-207323.txt