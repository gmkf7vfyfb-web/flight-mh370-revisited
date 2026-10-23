ids=['mem_5c7bbf306082','mem_8b868291ced6','mem_eafed062c92b','mem_acb6f1ca1275','mem_4943c40816b0','mem_f971d3fb5fee','mem_9edf139ac78e']
q=host.query("SELECT id, evidence, body FROM memories WHERE id IN (%s)" % ','.join("'%s'"%i for i in ids))
for r in q['rows']: print('\n##', r[0], r[1], '\n', r[2])