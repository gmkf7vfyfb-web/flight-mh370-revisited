ids=['mem_2c3c451c0993','mem_22d8763e0a29','mem_903c4aa1a08a','mem_95ab34caa99e','mem_fe151ba41363','mem_e8f3151ec665','mem_ab2d151ec171','mem_5e559775a7d5','mem_626a59b9ae20','mem_190e427bc715','mem_18360480ee29','mem_f51375722e87']
r=host.query("SELECT sql FROM sqlite_master WHERE name='memories'")
print(r)
