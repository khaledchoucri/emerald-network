# galsheet2.py DIR OUTPREFIX "m,..." [cols "0,6,12"] [rows-per-sheet]
import sys,os,re
from PIL import Image, ImageDraw
d,outp,ms=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].strip(',').split(',')]
ts=[int(x) for x in (sys.argv[4] if len(sys.argv)>4 else "0,6,12,18,24,36,48,66").split(',')]
per=int(sys.argv[5]) if len(sys.argv)>5 else 8
names={}
for l in open('/home/claude/pc/include/constants/moves.h'):
    m=re.match(r'#define MOVE_(\w+)\s+(\d+)',l)
    if m: names[int(m.group(2))]=m.group(1)
X0,X1,Y0,Y1=24,256,62,172
W,H=X1-X0,Y1-Y0
for s in range(0,len(ms),per):
    chunk=ms[s:s+per]
    img=Image.new('RGB',(len(ts)*(W+2)+84,len(chunk)*(H+2)),(10,10,20))
    dr=ImageDraw.Draw(img)
    for r,m in enumerate(chunk):
        dr.text((2,r*(H+2)+4),names.get(m,str(m))[:13],fill=(255,255,0))
        dr.text((2,r*(H+2)+16),str(m),fill=(200,200,200))
        for c,t in enumerate(ts):
            f=f'{d}/g_{m:03d}_{t:03d}.ppm'
            if not os.path.exists(f): continue
            im=Image.open(f).crop((X0,Y0,X1,Y1))
            img.paste(im,(84+c*(W+2),r*(H+2)))
            dr.text((84+c*(W+2)+2,r*(H+2)+2),str(t),fill=(255,255,255))
    img.save(f'{outp}_{s//per:02d}.png')
print('ok')
