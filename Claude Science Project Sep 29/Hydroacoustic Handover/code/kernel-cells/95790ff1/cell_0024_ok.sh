cd "repo/ISO Sept 28 Status/inputs/papers/hydroacoustics"; grep -o -E ".{50}(11[45][° .][0-9]|7[0-3]°|7[0-3] [0-9][0-9]\.|station (location|coordinat)|coordinates|latitude|longitude).{30}" ucrl-tr-207323.txt | grep -v -E "^.{0,10}(2001|2003)" | head; python3 - <<'EOF'
import pypdfium2 as p,re
d=p.PdfDocument("ucrl-tr-207323.pdf")
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    for m in re.finditer(r"(Ri.{0,3}e|dis.{0,4}imination|U.{1,4}L-ID|Crozet|H04|H08e|RiH)",t):
        pass
    if i+1 in (10,23,24): print(i+1, re.findall(r"Ri\w*e\b|dis\w*imination|U\w*L-ID",t))
EOF