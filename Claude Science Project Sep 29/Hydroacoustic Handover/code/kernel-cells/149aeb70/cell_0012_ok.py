for q in ["hydroacoustics composer test synthetic detection value of information",
          "hydroacoustics gate likelihood zero until detectability",
          "heavy lock policy threads allowance",
          "run I end of flight impact set hydroacoustics",
          "Kadri package detectability statement"]:
    r = host.search_memory(q) if hasattr(host,'search_memory') else None
    print("##", q, "->", "n/a" if r is None else "")
