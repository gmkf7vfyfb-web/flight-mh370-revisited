cd rr/drive; grep -n -E "N571|MEKAR|VAMPI|GIVAL|IGREX|EK ?343|UAE ?343|traffic in the|other flights" sir.txt | head -30
python -c "
import pypdf
r=pypdf.PdfReader('ig_malacca.pdf'); t='\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)); open('ig_malacca.txt','w').write(t); print(len(r.pages))"
grep -n -i -E "EK343|EK 343|Emirates|IndiGo|6E|other traffic|aircraft at|flight .* at" ig_malacca.txt | head -40