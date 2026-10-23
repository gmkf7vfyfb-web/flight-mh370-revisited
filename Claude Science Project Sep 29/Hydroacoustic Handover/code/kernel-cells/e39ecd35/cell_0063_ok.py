
for q in ["MH370 hydroacoustic signal impact Indian Ocean", "aircraft ocean impact energy hydroacoustic MH370 detection"]:
    r = host.mcp("literature","openalex_search_works", query=q, per_page=10)
    print("##",q)
    for w in r["records"][:10]:
        print("  ",w["publication_year"],"|",w["doi"],"|",(w["source"] or {}).get("display_name"),"|",w["title"][:95],"|",w.get("best_oa_pdf_url"))
