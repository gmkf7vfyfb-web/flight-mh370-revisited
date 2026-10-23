
import shutil, os, hashlib, pypdf
SRC='/Users/pete/Downloads/mh370-exchange/hydroacoustics/sources/open-access-fetched-2026-10-22'
os.makedirs(SRC, exist_ok=True)
names = {
 "10.1038_s41598-018-37626-z.pdf":"Kadri_2019_Effect_of_sea-bottom_elasticity_SciRep9-912_s41598-018-37626-z.pdf",
 "10.1017_jfm.2022.1091.pdf":"Williams_2023_Slender_rupture_elastic_seabed_JFM_jfm.2022.1091.pdf",
 "10.5194_nhess-7-243-2007.pdf":"Nosov_2007_Tokachi-oki_water_column_NHESS_7-243.pdf",
 "10.1038_s41597-024-04074-6.pdf":"Chu_Fan_2024_Global_undersea_acoustic_parameters_SciData_s41597-024-04074-6.pdf",
}
for k,v in names.items():
    s=os.path.join('articles',k)
    shutil.copy2(s, os.path.join(SRC,v)); shutil.copy2(s, v)
    h=hashlib.sha256(open(s,'rb').read()).hexdigest()[:12]
    r=pypdf.PdfReader(s)
    print(v[:60], len(r.pages),'pp', h, '|', (r.pages[0].extract_text() or '')[:80].replace('\n',' '))
