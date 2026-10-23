
r = host.mcp("literature","openalex_search_works", query="Poll Schumann estimation method fuel burn performance characteristics civil transport aircraft", per_page=10)
for w in r["records"]:
    print(w["publication_year"],"|",w["doi"],"|",(w["source"] or {}).get("display_name"),"|",w["title"][:100],"| OA:",w["open_access"]["oa_status"], w.get("best_oa_pdf_url"))
