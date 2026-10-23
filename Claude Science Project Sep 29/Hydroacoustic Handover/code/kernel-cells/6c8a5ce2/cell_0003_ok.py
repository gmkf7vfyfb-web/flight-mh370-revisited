for i in ['mem_21a9f09a83b0','mem_e586edc82fd8','mem_02043c16f970','mem_826a3d28bcb1','mem_16633a141f5e','mem_45f771c30f79','mem_eafed062c92b']:
    r=host.query("SELECT body,source_frame_id FROM memories WHERE id=?",[i])
    print(i, r['rows'][0][1]); print(r['rows'][0][0]); print('---')
