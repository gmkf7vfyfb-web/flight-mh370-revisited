
r = host.mcp("literature","openalex_search_works", query="An estimation method for the fuel burn and other performance characteristics of civil transport aircraft Part 2 determining the aircraft's characteristic parameters", per_page=5)
for w in r["records"][:5]:
    print(w["publication_year"],"|",w["doi"],"|",w["title"][:120],"|",w.get("best_oa_pdf_url"))
