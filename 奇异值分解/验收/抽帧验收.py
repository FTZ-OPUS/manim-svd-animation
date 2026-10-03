from pathlib import Path
import av,json,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
path=Path(sys.argv[1])
timeline=json.loads((ROOT/'验收/时间轴.json').read_text())
out=ROOT/'验收'/sys.argv[2]
out.mkdir(exist_ok=True)
frames=[]
for item in timeline:
    c=av.open(str(path));t=item['sample']
    c.seek(int(t*av.time_base))
    for f in c.decode(video=0):
        if float(f.time)>=t:
            image=f.to_image();image.save(out/f"{item['index']:02d}.png")
            frames.append((item,image));break
    c.close()
for page in range((len(frames)+3)//4):
    sheet=Image.new('RGB',(1920,1120),(18,24,31));d=ImageDraw.Draw(sheet)
    for j,(item,im) in enumerate(frames[page*4:page*4+4]):
        im=im.resize((960,540))
        x=(j%2)*960;y=(j//2)*560
        sheet.paste(im,(x,y+20));d.text((x+15,y+4),f"{item['index']:02d} / {item['sample']:.2f}s",fill='white')
    sheet.save(out/f'sheet_{page+1}.jpg',quality=94)
c=av.open(str(path));s=c.streams.video[0]
info=dict(duration=c.duration/av.time_base,width=s.width,height=s.height,fps=float(s.average_rate),size_MB=path.stat().st_size/1024**2,chapters=len(frames))
(out/'metadata.json').write_text(json.dumps(info,indent=2));print(json.dumps(info));c.close()
