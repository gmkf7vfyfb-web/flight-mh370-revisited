
for p in [27,29]:
    img=pdf[p-1].render(scale=2.5).to_pil(); img.save(f'audit/pages/p{p}.png')
print(open("audit/hb/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt").read().split('\n')[311][:1500])
