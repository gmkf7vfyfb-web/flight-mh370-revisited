
import pypdfium2 as pdfium, pandas as pd, glob
d="hrepo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces/"
for p in "abcde":
    f=glob.glob(d+f"*panel-{p}-*")[0]; x=pd.read_csv(f); print(p, x.utc.iloc[0], x.utc.iloc[-1])
pth=host.artifact_path("e6fa6f46-4c0e-4c54-b53a-cb594bed0308")
pdf=pdfium.PdfDocument(pth); txt=[pdf[i].get_textpage().get_text_range() for i in range(len(pdf))]
open('royer.txt','w').write("\n\n=====PAGE=====\n".join(txt)); print(len(pdf), [len(t) for t in txt])
