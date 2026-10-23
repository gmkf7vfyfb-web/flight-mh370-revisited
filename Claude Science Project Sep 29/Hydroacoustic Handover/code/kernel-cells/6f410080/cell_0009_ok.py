for k in ['factual','marghany','guardian']:
    print('#####',k); print(open(f'handoff/{k}_psnip.txt').read()[:5000])
print(open('handoff/marghany.txt').read()[:2500])