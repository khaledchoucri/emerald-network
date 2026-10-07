import sys, colorsys
from PIL import Image
G='/home/claude/pc/graphics/pokemon/'
def load(n):
    im=Image.open(G+n+'/front.png'); pal=[tuple(int(x) for x in l.split()) for l in open(G+n+'/normal.pal').read().split('\n')[3:19]]
    px=im.load(); w,h=im.size; h=min(h,64)
    idx=[[px[x,y] for x in range(w)] for y in range(h)]
    return idx,pal,w,h
def ramps(idx,pal):
    cnt=[0]*16
    for r in idx:
        for i in r: cnt[i]+=1
    cols=[]
    for i in range(1,16):
        if cnt[i]==0: continue
        r,g,b=[c/255 for c in pal[i]]; hh,l,s=colorsys.rgb_to_hls(r,g,b)
        cols.append((i,hh,l,s,cnt[i]))
    # neutral: very dark outline / near white / low saturation
    neutral=[c for c in cols if c[3]<0.18 or c[2]<0.12 or c[2]>0.93]
    chroma=[c for c in cols if c not in neutral]
    groups=[]
    for c in sorted(chroma,key=lambda c:-c[4]):
        for g in groups:
            d=min(abs(c[1]-g[0][1]),1-abs(c[1]-g[0][1]))
            if d<0.07: g.append(c); break
        else: groups.append([c])
    groups.sort(key=lambda g:-sum(c[4] for c in g))
    return groups,neutral
def recolor(bodyn,headn):
    bi,bp,w,h=load(bodyn); hi,hp,_,_=load(headn)
    bg,_=ramps(bi,bp); hg,_=ramps(hi,hp)
    m={}
    for k,g in enumerate(bg):
        if not hg: break
        tg=sorted(hg[k%len(hg)],key=lambda c:c[2]); g=sorted(g,key=lambda c:c[2])
        for j,c in enumerate(g):
            t=tg[round(j*(len(tg)-1)/max(1,len(g)-1))] if len(tg)>1 else tg[0]
            # keep body's lightness ramp, take head's hue/sat
            r,gg,b=colorsys.hls_to_rgb(t[1],c[2],t[3])
            m[c[0]]=(int(r*255),int(gg*255),int(b*255))
    out=Image.new('RGBA',(w,h))
    for y in range(h):
        for x in range(w):
            i=bi[y][x]
            if i==0: continue
            out.putpixel((x,y),(*m.get(i,bp[i]),255))
    return out
def plain(n):
    i,p,w,h=load(n); out=Image.new('RGBA',(w,h))
    for y in range(h):
        for x in range(w):
            if i[y][x]: out.putpixel((x,y),(*p[i[y][x]],255))
    return out
def headbody(bodyn,headn):
    body=recolor(bodyn,headn); head=plain(headn)
    bb=body.getbbox(); hb=head.getbbox()
    hh=int((hb[3]-hb[1])*0.42); hcrop=head.crop((hb[0],hb[1],hb[2],hb[1]+hh))
    tw=int((bb[2]-bb[0])*0.6); sc=tw/hcrop.size[0]
    hcrop=hcrop.resize((max(1,tw),max(1,int(hh*sc))),Image.NEAREST)
    out=body.copy(); x=(bb[0]+bb[2])//2-hcrop.size[0]//2; y=bb[1]-hcrop.size[1]//3
    out.alpha_composite(hcrop,(max(0,x),max(0,y)))
    return out
pairs=[('swampert','pelipper'),('blaziken','manectric'),('gardevoir','altaria'),('aggron','metagross'),('sceptile','flygon')]
W=64;S=3
sheet=Image.new('RGBA',(W*S*4+30,W*S*len(pairs)+10),(30,34,48,255))
for r,(a,b) in enumerate(pairs):
    for c,im in enumerate([plain(a),plain(b),recolor(a,b),headbody(a,b)]):
        sheet.alpha_composite(im.resize((W*S,W*S),Image.NEAREST),(c*(W*S+10),r*W*S+5))
sheet.save('/tmp/fuse/sheet.png')
