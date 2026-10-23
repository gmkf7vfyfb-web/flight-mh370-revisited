cat > q1b.md <<'EOF'
## Q1b. Indian radars that could have been in range after 18:22 UTC

**Short answer.** No official Indian source lists the air-surveillance radars on the Andaman and Nicobar Islands in 2014, their types or their instrumented ranges: **NOT FOUND**. Only the military airfields that could host such radars have published positions. These are, from north to south: INS Kohassa (Shibpur, Diglipur), INS Utkrosh (Port Blair, shared with the civil airport VOPB), Car Nicobar Air Force Station (VOCX) and INS Baaz (Campbell Bay, Great Nicobar; commissioned 31 July 2012). INS Kardip (Kamorta) is a naval base without an airfield, and I found no published coordinates for it. Antenna sites and heights are not published, so the airfield coordinates below are **proxies**, not radar positions. For operating status that night, the only on-record statement is by Rear Admiral Sudhir Pillai, chief of staff of the Andaman and Nicobar Command, to Reuters (about 15–16 March 2014). He said "We have many radar systems operating in this area, but nothing was picked up" and that it was possible the military radars were switched off "as we operate on an 'as required' basis". A separate defence source said India did not keep radars on at all times because of cost [press, Reuters]. A Defence Ministry official, unnamed, later called the idea of a flight through Indian airspace undetected "bizarre" [press, Reuters via Malay Mail, 18 Mar 2014]. Indian sources told the Tribune (17 Mar 2014) that the southern Indian Ocean has "no radar coverage". I found no later formal Indian statement, report or answer in Parliament on Andaman radar status on 7–8 March 2014: **NOT FOUND**. For Port Blair civil ATC, the AAI airport page currently lists "Surveillance: ARSR + MSSR" with the value field shown as "-". I found no source for a Port Blair civil radar or its range in 2014: **NOT FOUND**. Any secondary (MSSR) radar is irrelevant after 17:21, because MH370's transponder was off; only a primary radar could have seen the aircraft. A 2014 blog comment says the Car Nicobar radar was destroyed in the 2004 tsunami and replaced only by an unmanned-at-night mobile radar. This is unverified [independent analyst].

### Q1b data table: candidate Indian sites (airfield reference points; radar positions not published)

| Site | Operator | Latitude | Longitude | Radar type / range | Source of position |
|---|---|---|---|---|---|
| INS Kohassa, Shibpur (Diglipur), North Andaman (ICAO VODX) | Indian Navy (ANC) | 13.237982 N | 93.049944 E | NOT FOUND | Wikipedia coordinates (API, 17 Oct 2026) |
| INS Utkrosh / Veer Savarkar Intl, Port Blair (VOPB) | Indian Navy; civil enclave AAI | 11.64111 N (11°38′28″) | 92.72972 E (092°43′47″) | Military: NOT FOUND (a PAR is mentioned, not dated). Civil: AAI page "ARSR + MSSR · -"; 2014 status NOT FOUND | Wikipedia (DAFIF) |
| Car Nicobar AFS (VOCX) | Indian Air Force | 9.1525 N | 92.8196 E | NOT FOUND (2004 tsunami loss claimed in a blog comment only) | airport database line quoted on Wikipedia (lower precision) |
| INS Baaz, Campbell Bay, Great Nicobar (VOBX) | Indian Navy | 7.01306 N (7°0′47″) | 93.92361 E (93°55′25″) | NOT FOUND ("radar systems" mentioned without type) | Wikipedia |
| INS Kardip, Kamorta | Indian Navy | NOT FOUND | NOT FOUND | NOT FOUND | — |

Notes on the table:
- **Radar-horizon inputs.** With the standard 4/3-Earth refraction, d [NM] ≈ 1.23 (√h_antenna[ft] + √h_target[ft]). FL350 alone gives 1.23 × √35,000 ≈ 230 NM. Each 100 ft of antenna height adds about 12 NM. Antenna heights are NOT FOUND, so a sensitivity range of 0–300 ft (about 0–21 NM extra) is a reasonable bracket. Island terrain (Saddle Peak 732 m on North Andaman; Mount Thullier 642 m on Great Nicobar) could raise or mask individual sites. These heights are not from a source read for this review, so treat them as context, not inputs.
- **Generic AAI range figures.** The AAI's published figure for its en-route ARSR/MSSR installations is 250 NM (AAI Northern Region page; Thiruvananthapuram MSSR-1 press release: "maximum range of 250 NM"). These are generic AAI figures, not Andaman figures.
- **Not air-surveillance.** The Coastal Radar Network / ICSS stations on the islands are surface-search radars. Their 2014 status is unknown, and they are not air-surveillance radars.

**Obtainable and how.**
- Indian military radar positions, types and recordings for 7–8 March 2014: **not available**. Request via the Ministry of Defence or Andaman and Nicobar Command (through the Malaysian investigation or a diplomatic channel); release is unlikely.
- Port Blair civil surveillance equipment in 2014: **request from AAI**, or consult the AIP India ENR 1.6 / AD 2 VOPB entries of 2014 (AIP archive; not checked here).
EOF
python - <<'EOF'
md=open('research-radar-infrasound-ohasisbio.md').read()
q1b=open('q1b.md').read()
anchor='---\n\n## Q2.'
assert md.count(anchor)==1
md=md.replace(anchor, q1b+'\n'+anchor)
# sources
src_add='''- [15] Wikipedia, INS Kohassa / INS Utkrosh / INS Baaz / Car Nicobar Air Force Station / Andaman and Nicobar Command (coordinates via the Wikipedia API, 17 Oct 2026). https://en.wikipedia.org/wiki/INS_Kohassa ; https://en.wikipedia.org/wiki/INS_Utkrosh ; https://en.wikipedia.org/wiki/INS_Baaz ; https://en.wikipedia.org/wiki/Car_Nicobar_Air_Force_Station ; https://en.wikipedia.org/wiki/Andaman_and_Nicobar_Command
- [16] Malay Mail / Reuters, 18 Mar 2014 (Indian defence ministry official). https://www.malaymail.com/news/malaysia/2014/03/18/taliban-deny-involvement-in-mh370/637201
- [17] The Tribune (India), 17 Mar 2014. https://www.tribuneindia.com/2014/20140317/main1.htm
- [18] AAI, Sri Vijaya Puram (Port Blair) airport page. https://www.aai.aero/en/node/2933 ; AAI Northern Region page (ARSR/MSSR 250 NM). https://www.aai.aero/en/node/8849 ; AAI press release, Thiruvananthapuram MSSR-1. https://www.aai.aero/sites/default/files/AAI_PR_Trivedrum_17Sep.pdf
- [19] Livefist, 20 Mar 2014 (Andaman radars "operate intermittently"; commentary). https://www.livefistdefence.com/mh370-switched-off-radars-security/
- [20] Comment on Wise (2014) claiming the Car Nicobar radar was lost in 2004 (unverified). http://www.jeffwise.net/2014/11/18/mh370-and-the-mystery-of-indonesian-radar/comment-page-1/
'''
a='- [14] AFP, 19 Mar 2014'
i=md.index(a); j=md.index('\n',i)
md=md[:j+1]+src_add+md[j+1:]
ob='- **Thai military radar plots:**'
md=md.replace(ob,'- **Indian Andaman & Nicobar radar positions, types, recordings (Q1b):** not available. Request via the MoD / Andaman and Nicobar Command; Port Blair civil equipment from AAI or the 2014 AIP India.\n'+ob)
md=md.replace('- The Q3 energy comparison','- Q1b (Indian radar sites): no official site list exists publicly. Positions given are airfield reference points used as proxies for radar sites.\n- The Q3 energy comparison')
open('research-radar-infrasound-ohasisbio.md','w').write(md)
print(len(md.split()))
EOF
grep -n "^## " research-radar-infrasound-ohasisbio.md