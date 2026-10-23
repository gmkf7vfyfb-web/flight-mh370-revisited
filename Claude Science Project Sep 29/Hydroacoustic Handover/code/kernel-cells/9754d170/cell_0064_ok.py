
for p_ in [30,33]:
    img=pdf[p_-1].render(scale=1.3).to_pil(); img.save(f'audit/pages/p{p_}.png')
