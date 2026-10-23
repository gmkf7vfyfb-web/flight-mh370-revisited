from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm, shutil
fpath=fm.findfont(fm.FontProperties(family='DejaVu Sans',weight='bold'))
os.makedirs('withdrawn',exist_ok=True)
png=ART[ART.filename.str.endswith('.png')]
L1="WITHDRAWN 23 Oct 2026 - DO NOT USE"
L2="Built from detector outputs at noise level. No record shows an impact signal at the predicted times. See hydroacoustics-candidates-withdrawal-2026-10-23.md"
done=[]
for _,r in png.iterrows():
    im=Image.open(host.artifact_path(r.latest_version_id)).convert('RGB'); W_,H_=im.size
    bh=int(max(90,W_*0.06)); out=Image.new('RGB',(W_,H_+bh),'white'); out.paste(im,(0,bh))
    d=ImageDraw.Draw(out); d.rectangle([0,0,W_,bh],fill=(165,15,21))
    f1=ImageFont.truetype(fpath,int(bh*0.38)); f2=ImageFont.truetype(fpath,int(bh*0.17))
    while d.textlength(L2,font=f2)>W_*0.97: f2=ImageFont.truetype(fpath,f2.size-1)
    d.text((W_*0.015,bh*0.08),L1,font=f1,fill='white'); d.text((W_*0.015,bh*0.62),L2,font=f2,fill='white')
    # diagonal watermark
    wm=Image.new('RGBA',out.size,(0,0,0,0)); dw=ImageDraw.Draw(wm)
    fw_=ImageFont.truetype(fpath,int(min(W_,H_)*0.16)); txt='WITHDRAWN'
    tw=dw.textlength(txt,font=fw_); dw.text(((W_-tw)/2,(H_+bh)/2-fw_.size/2),txt,font=fw_,fill=(165,15,21,70))
    wm=wm.rotate(30,center=(W_/2,(H_+bh)/2))
    out=Image.alpha_composite(out.convert('RGBA'),wm).convert('RGB')
    fn=f'withdrawn/{r.filename}'; out.save(fn); done.append((fn,r.id))
print(len(done)); print(done[0])