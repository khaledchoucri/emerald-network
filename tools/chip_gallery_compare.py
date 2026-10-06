import sys,os,re
from PIL import Image, ImageDraw
before,after,out=sys.argv[1],sys.argv[2],sys.argv[3]
ms=[int(x) for x in sys.argv[4].split(',')]
ts=[int(x) for x in sys.argv[5].split(',')]
names={}
for l in open('/home/claude/pc/include/constants/moves.h'):
    m=re.match(r'#define MOVE_(\w+)\s+(\d+)',l)
    if m: names[int(m.group(2))]=m.group(1)
X0,X1,Y0,Y1=24,256,66,170
W,H=X1-X0,Y1-Y0
img=Image.new('RGB',(len(ts)*(W+2)+96,len(ms)*2*(H+2)+len(ms)*6),(12,12,22))
dr=ImageDraw.Draw(img)
y=0
for m in ms:
    for k,(d,lab) in enumerate(((before,'before'),(after,'after'))):
        dr.text((2,y+4),names.get(m,str(m))[:14],fill=(255,255,0))
        dr.text((2,y+18),lab,fill=(255,140,140) if k==0 else (140,255,140))
        for c,t in enumerate(ts):
            f=f'{d}/g_{m:03d}_{t:03d}.ppm'
            if os.path.exists(f):
                img.paste(Image.open(f).crop((X0,Y0,X1,Y1)),(96+c*(W+2),y))
            dr.text((96+c*(W+2)+2,y+2),f't={t}',fill=(255,255,255))
        y+=H+2
    y+=6
img.save(out); print(img.size)
