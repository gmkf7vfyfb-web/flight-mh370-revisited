ids=['mem_4aba6efdb522','mem_c85d94cab818','mem_13b941878e9b','mem_e9d437957a23','mem_44c1625bddcd','mem_56d226ed688c','mem_68e3e0f76b2d','mem_16df2afcc40c','mem_b14551be66d1','mem_b9838afcd7f8','mem_a46ec557e204','mem_e653e85a1bc4','mem_7d3716de6ffd','mem_4b4418db3c23','mem_42467aabb5f1','mem_4bdce496f7a6','mem_93d5135317c3','mem_2f93e44158f7','mem_b75d82bda754','mem_dad7288dfba4','mem_02043c16f970','mem_eeee80e90389']
r=host.query("SELECT sql FROM sqlite_master WHERE name='memories'")
print(r)
