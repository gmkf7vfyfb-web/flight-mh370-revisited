s=open(p).read().replace("icao2015wp30","icao2014wp30").replace("ICAO WP/30","ICAO ATM/SG/2-WP30"); open(p,"w").write(s)
W="http://web.archive.org/web/"
J="www.jacc.gov.au/media/"
def jm(key,num,date,title,ts,path,note):
    return f"""@misc{{{key},
  author = {{{{Joint Agency Coordination Centre}}}},
  title = {{{title}}},
  year = {{2014}}, note = {{{date}. {note} Archived snapshot {ts}. Grade A (read via Internet Archive, 18 Oct 2026)}},
  url = {{{W}{ts}/http://{J}{path}}}, urldate = {{2026-10-18}}
}}"""
bib=[]
bib.append("""% sources-sightings leg, Kadri-Haixun conditional test (18 Oct 2026). Keys atsb2017operational and mot2018mh370 reuse paper/references.bib.
@techreport{atsb2017operational,
  author = {{Australian Transport Safety Bureau}}, title = {The Operational Search for {MH370}},
  institution = {Australian Transport Safety Bureau}, number = {AE-2014-054}, year = {2017}, month = oct, address = {Canberra},
  note = {Read pp. 29--41 and 116--119 (printed = PDF - 9) from the project Drive text copy. Grade A}
}
@techreport{atsb2015searchareas,
  author = {{Australian Transport Safety Bureau}}, title = {{MH370} -- Definition of Underwater Search Areas},
  institution = {Australian Transport Safety Bureau}, number = {AE-2014-054}, year = {2014}, address = {Canberra},
  note = {26 June 2014, updated 30 July 2015. Read pp. 11--13 (printed = PDF - 5), Drive copy. Grade A},
  url = {https://www.atsb.gov.au/sites/default/files/media/5668327/ae2014054_mh370__search_areas_30jul2015.pdf}
}
@techreport{mot2015factual,
  author = {{Malaysian ICAO Annex 13 Safety Investigation Team for MH370}},
  title = {Factual Information: Safety Investigation for {MH370}, Malaysia Airlines {MH370} Boeing {B777-200ER} (9M-MRO), 08 March 2014},
  institution = {Ministry of Transport Malaysia}, number = {MH370/01/15}, year = {2015}, month = mar,
  note = {Issued 8 March 2015. Read section 1.11.3, pp. 59--60. Grade A}
}
@techreport{mot2018mh370,
  author = {{Malaysian ICAO Annex 13 Safety Investigation Team for MH370}},
  title = {Safety Investigation Report, {Malaysia Airlines Boeing B777-200ER (9M-MRO)}, 08 March 2014},
  institution = {Ministry of Transport Malaysia}, number = {MH370/01/2018}, year = {2018}, month = jul,
  note = {Issued 02 July 2018. Read pp. 136--137, 364--365 (ULB). Grade A}
}
@misc{icao2014wp30,
  author = {{Australia}}, title = {{MH370} Search and Rescue Response -- {JRCC} Australia},
  howpublished = {ICAO APANPIRG ATM Sub-Group, Second Meeting (ATM/SG/2), Hong Kong, 4--8 August 2014, Working Paper WP30},
  year = {2014}, note = {Read paras 2.22--2.26. Grade A}
}""")
bib.append(jm("jacc2014mr010","mr010","5--6 April 2014","Media Reporting on Chinese Ship Detection of Electronic Pulse Signals","20140405191319","releases/2014/april/mr010.aspx","White objects about 90 km from the detection area."))
for k,ts,d in [("mr011","20140406022110","6 April 2014 am"),("mr012","20140408003033","7 April 2014 am"),("mr013","20140408082504","8 April 2014 am"),("mr014","20140411012617","9 April 2014 am"),("mr015","20140411122014","10 April 2014 am")]:
    bib.append(jm("jacc2014"+k,k,d,"Search and recovery continues for Malaysian flight {MH370}",ts,f"releases/2014/april/{k}.aspx","Media release."))
for k,ts,d,ti in [("tr006","20140408000655","6 April 2014","Transcript of Press Conference, 6 April 2014"),("tr007","20140408153652","7 April 2014","Transcript of Press Conference, 7 April 2014"),
                  ("tr008","20140412010244","9 April 2014","Transcript of Press Conference, 9 April 2014"),("tr009","20140415082809","14 April 2014","Transcript of Press Conference, 14 April 2014")]:
    bib.append(jm("jacc2014"+k,k,d,ti,ts,f"interviews/2014/april/{k}.aspx","Air Chief Marshal A. Houston (Ret'd)."))
bib.append(jm("jacc2014map012","map","7 April 2014","Position of signals received by Hai Xun 01 (5 April 2014) and Ocean Shield (6 April 2014) [map]","20140407112329","releases/2014/april/mr_012-1.jpg","AMSA map attached to mr012."))
bib.append(jm("jacc2014map013","map","8 April 2014","Planned search areas 08 April 2014, sonobuoy search 250 sq km [map]","20150318144905","releases/2014/april/mr_013-5.jpg","AMSA map attached to mr013."))
bib.append("""@misc{ukmod2014echo,
  author = {{UK Ministry of Defence}}, title = {{HMS} Echo continues hunt for missing Malaysian airliner}, year = {2014}, note = {14 April 2014. Read as search extract only. Grade B},
  url = {https://www.globalsecurity.org/military/library/news/2014/04/mil-140414-ukmod02.htm}, urldate = {2026-10-18}
}
@misc{ukmod2014tireless,
  author = {{UK Ministry of Defence}}, title = {{HMS} Tireless stands down in search for missing aircraft}, year = {2014}, note = {24 April 2014. Read as search extract only. Grade B},
  url = {https://www.gov.uk/government/news/hms-tireless-stands-down-in-search-for-missing-aircraft}, urldate = {2026-10-18}
}
@misc{xinhua2014pulse,
  author = {{Xinhua}}, title = {Chinese ship searching for {MH370} detects pulse signal (as carried by CGTN America)}, year = {2014}, note = {5 April 2014; quotes China Maritime Search and Rescue Center. Grade C},
  url = {https://america.cgtn.com/2014/04/05/chinese-ship-searching-for-missing-jet-detects-pulse-signal/}, urldate = {2026-10-18}
}
@misc{sina2014haixun,
  author = {{Sina Military}}, title = {Zhongguo haixun chuan lianxu 2 tian faxian yisi {MH370} heixiazi xinhao [Chinese patrol ship detects suspected MH370 black-box signal on two consecutive days]}, year = {2014},
  note = {6 April 2014; cites CCTV. In Chinese. Grade C}, url = {https://mil.news.sina.com.cn/2014-04-06/0838772468.html}, urldate = {2026-10-18}
}
@misc{xinmin2014haixun,
  author = {{Xinmin Evening News}}, title = {Haixun 01 2 tian 2 ci tingdao heixiazi maichong xinhao [Haixun 01 hears black-box pulse twice in two days]}, year = {2014},
  note = {5 April 2014, via China News Service. In Chinese. Grade C}, url = {https://www.chinanews.com.cn/gn/2014/04-05/6034302.shtml}, urldate = {2026-10-18}
}
@misc{people2014floating,
  author = {{People's Daily / Xinhua}}, title = {Wo soujiu chuan tingdao yisi heixiazi xinhao [Our rescue ship hears suspected black-box signal]}, year = {2014},
  note = {6 April 2014; PLAAF white floating objects from 11:05, photographed. In Chinese. Grade C}, url = {http://cpc.people.com.cn/n/2014/0406/c87228-24835605.html}, urldate = {2026-10-18}
}
@misc{cn12371_2014,
  author = {{Xinhua / PLA Daily, via 12371.cn}}, title = {Zhongguo kongjun zai nan Yinduyang faxian piaofuwu [Chinese Air Force finds floating objects in the southern Indian Ocean]}, year = {2014},
  note = {6 April 2014; departure 06:04, task area more than 2,700 km from Perth, objects from 11:05 over 20 min; PLAN task area 20--26 S, 101--104 E from 4 April. In Chinese. Grade C},
  url = {https://news.12371.cn/2014/04/06/ARTI1396738988082649.shtml}, urldate = {2026-10-18}
}
@misc{globaltimes2014expanded,
  author = {{Global Times}}, title = {Ships try to pick up suspicious signals detected by Haixun 01}, year = {2014}, note = {8 April 2014; 432 sq km expanded area. Grade C},
  url = {https://www.globaltimes.cn/content/853171.shtml}, urldate = {2026-10-18}
}
@misc{pti2014deccan,
  author = {{Press Trust of India}}, title = {Missing jet: Chinese ship detects pulse signal}, howpublished = {Deccan Herald}, year = {2014}, note = {5 April 2014; Liberation Daily: signals not recorded. Grade C},
  url = {https://www.deccanherald.com/archives/missing-jet-chinese-ship-detects-2185601}, urldate = {2026-10-18}
}
@misc{ap2014handheld,
  author = {{Associated Press}}, title = {Ships race to site of signal in jet search}, howpublished = {The Denver Post}, year = {2014}, note = {7 April 2014; CCTV footage of pole-mounted detector. Grade C},
  url = {https://www.pressreader.com/usa/the-denver-post/20140407/281500749225589}, urldate = {2026-10-18}
}
@misc{ulich2018north25,
  author = {Ulich, Bobby}, title = {Search for {MH370} north of 25S unlikely}, year = {2018}, note = {Independent analyst note, project Drive copy. Grade C}
}
@misc{nasacmr2026,
  author = {{NASA Earthdata}}, title = {Common Metadata Repository granule search: MOD02QKM, MYD02QKM v6.1, VNP02IMG, ASTER L1T, EO-1, Sentinel-1A (ASF)}, year = {2026},
  note = {Queried 18 October 2026, box 100--102.5 E, 25--26.5 S, 8 March--30 April 2014}, url = {https://cmr.earthdata.nasa.gov/search}, urldate = {2026-10-18}
}
@misc{nasacsda2026,
  author = {{NASA Commercial SmallSat Data Acquisition Program}}, title = {{CSDA} Maxar {L1B} collections ({WV01}, {WV02}, {GE01}, {QB02}, {IKONOS}) in {CMR}}, year = {2026},
  note = {Queried 18 October 2026; a subset of the Maxar archive}, url = {https://cmr.earthdata.nasa.gov/search}, urldate = {2026-10-18}
}
@misc{usgsstac2026,
  author = {{U.S. Geological Survey}}, title = {Landsat Collection 2 Level-1 {STAC} catalogue (landsat-c2l1)}, year = {2026},
  note = {Queried 18 October 2026}, url = {https://landsatlook.usgs.gov/stac-server}, urldate = {2026-10-18}
}
@misc{cdse2026,
  author = {{European Space Agency}}, title = {Copernicus Data Space Ecosystem {OData} catalogue}, year = {2026},
  note = {Queried 18 October 2026}, url = {https://catalogue.dataspace.copernicus.eu/odata/v1}, urldate = {2026-10-18}
}
@misc{celestrak2026,
  author = {Kelso, T. S.}, title = {{CelesTrak} {SATCAT}}, year = {2026}, note = {Launch and decay dates read 18 October 2026}, url = {https://celestrak.org/satcat/}, urldate = {2026-10-18}
}""")
open("out/sources-sightings-references.bib","w").write("\n".join(bib)+"\n")
print(len(re.findall(r"^@",open("out/sources-sightings-references.bib").read(),re.M)))