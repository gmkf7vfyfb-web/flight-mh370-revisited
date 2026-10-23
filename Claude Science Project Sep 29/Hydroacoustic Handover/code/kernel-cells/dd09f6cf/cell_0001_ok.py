ids=['mem_3a43dbfd5e36','mem_152b9a17f448','mem_2093512c9df7','mem_a16bea5ba964','mem_e24512f7f201','mem_6f80cca51aff','mem_ab0b71b7305e','mem_be40f81c24dc','mem_d6ac83fa3ced','mem_ead98a03ab31','mem_1e616795c12f','mem_c9de902931d6']
r=host.query("SELECT sql FROM sqlite_master WHERE name='memories'")
print(r)
