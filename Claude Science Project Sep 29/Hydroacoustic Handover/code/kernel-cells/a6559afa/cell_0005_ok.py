ids_over = [r[0] for r in f['rows'] if r[1]=='676a6e64-2eac-490f-b67d-6c3f5c82f047']
tot = {r[0]:r[9] for r in f['rows']}
print(len(ids_over), round(sum(tot[i] for i in ids_over),1), round(tot['676a6e64-2eac-490f-b67d-6c3f5c82f047'],1), round(tot['a35831fe-107a-4961-bc9f-e6fd6d255601'],1), round(tot['0bb05edc-67da-48f0-9322-bf94577b110d'],1))