ids=['mem_6ed27ad5441f','mem_41cbe96f06c4','mem_c08d69625ed1','mem_22bec808b159','mem_74e8ca53358a','mem_82ebb617feec','mem_a8f8f09154ed','mem_2500ea862b9c','mem_281f2eda7f6e','mem_853e9f6853a9','mem_20bbb3bbee11','mem_c0f3024ddbe6']
r=host.query("SELECT sql FROM sqlite_master WHERE name='memories'")
print(r['rows'][0][0][:600])
