import fitz
doc=fitz.open(host.artifact_path("3b556efc-d3fb-4ce6-b233-bfdd66cf809c"))
hits=[(i+1, doc[i].get_text()[:0]) for i in range(len(doc)) if "Figure 2." in doc[i].get_text() or "Figure 2 " in doc[i].get_text()]
print(len(doc), [h[0] for h in hits])
for pno,_ in hits[:2]:
    t=doc[pno-1].get_text(); j=t.find("Figure 2"); print(pno, repr(t[j:j+500]))
pg=doc[hits[0][0]-1]; pix=pg.get_pixmap(dpi=200); pix.save("hydro/blackman_p_fig2.png"); print(pix.width,pix.height)