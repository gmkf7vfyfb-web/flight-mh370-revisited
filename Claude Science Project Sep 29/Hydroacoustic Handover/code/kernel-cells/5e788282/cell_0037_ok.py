from PIL import Image
import io
def getimg(doc,xref):
    d=doc.extract_image(xref); im=Image.open(io.BytesIO(d['image'])).convert('RGB'); return np.array(im), d
A5,d5=getimg(fd,53); A4,d4=getimg(fd,42)
print(A5.shape, d5['ext'], d5.get('colorspace'), A4.shape)
Image.fromarray(A5).save("metz_fig3AB_raw.png"); Image.fromarray(A4).save("metz_fig2AD_raw.png")
# find dark frame lines: rows/cols where many pixels are dark grey
dark=(A5.sum(2)<200)
print("rows dark frac>0.3:", np.where(dark.mean(1)>0.3)[0][:20], np.where(dark.mean(1)>0.3)[0][-10:])
cols=np.where(dark.mean(0)>0.5)[0]; print("cols:",cols)
s7=strokes(6); L7=[l for l in s7 if l[0]!='re' and (abs(l[0]-l[2])>50 or abs(l[1]-l[3])>30)]; print(sorted(set(L7))[:12])
sh7=[l for l in s7 if l[0]!='re' and l not in L7]
print(sorted(set(l[0] for l in sh7 if l[0]==l[2])), sorted(set(l[1] for l in sh7 if l[1]==l[3])))