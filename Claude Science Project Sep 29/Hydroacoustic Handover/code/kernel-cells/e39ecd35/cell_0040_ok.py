
import json
def ls(q, n=50):
    r = host.mcp("literature","openalex_search_works", query=q, per_page=n)
    for w in r["records"]:
        print(w["publication_year"], "|", w["doi"], "|", (w["source"] or {}).get("display_name"), "|", w["title"][:95])
    print("---", r["api_total"])
ls("MH370 descent end of flight")
