from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,shutil
D=Path(__file__).resolve().parent
R=Image.open(D/'raw/custom_parts_generated.png').convert('RGBA')
G=['#202020','#585858','#909090','#c8c8c8','#ffffff']
GOLD=['#0b0a14','#554016','#af842a','#e3b650','#ffe7a0']
MAG=['#0b0a14','#161b2d','#460c35','#8b1b58','#c9007c','#fa2d98','#ff65a5','#ffa6d1']
def rgb(p):return np.array([tuple(bytes.fromhex(s[1:])) for s in p],dtype=np.int32)
def quant(im,p):
 a=np.array(im.convert('RGBA')); ds=((a[:,:,:3,None].astype(np.int32)-rgb(p).T[None,None,:,:])**2).sum(axis=2);ix=ds.argmin(axis=2)
 out=np.concatenate([rgb(p)[ix].astype('uint8'),np.where(a[:,:,3:4]>=128,255,0).astype('uint8')],axis=2);out[out[:,:,3]==0,:3]=0
 return Image.fromarray(out,'RGBA')
def normalize(crop,size,p,k,fill):
 # Crop source silhouette at native resolution; retain its corner shapes, replace noisy/ornamented middle runs.
 im=quant(R.crop(crop).resize(size,Image.Resampling.NEAREST),p);a=np.array(im);w,h=size
 a[:k,k:w-k]=a[:k,w//2:w//2+1]
 a[h-k:,k:w-k]=a[h-k:,w//2:w//2+1]
 # Sample side at 1/4 height, outside source's ornamental waist; every edge becomes uniform for 9-slicing.
 yy=k+2
 a[k:h-k,:k]=a[yy:yy+1,:k]
 a[k:h-k,w-k:]=a[yy:yy+1,w-k:]
 a[k:h-k,k:w-k]=tuple(bytes.fromhex(fill[1:]))+(255,)
 return Image.fromarray(a,'RGBA')
def recolor(im,src,dst):
 a=np.array(im);b=a.copy()
 for s,t in zip(rgb(src),rgb(dst)):
  mask=(a[:,:,:3]==s).all(2)&(a[:,:,3]>0);b[mask,:3]=t
 return Image.fromarray(b,'RGBA')
def save(name,im):
 im.save(D/(name+'.png'));im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(D/(name+'_review_4x.png'));im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.NEAREST).save(D/(name+'_half.png'))
def row(ims,gap=8):
 out=Image.new('RGBA',(sum(i.width for i in ims)+gap*(len(ims)-1),max(i.height for i in ims)));x=0
 for im in ims:out.paste(im,(x,0));x+=im.width+gap
 return out
# C1 correction, preserving v001 and every C2 byte.
a=np.array(Image.open(D.parent/'v001/window_body.png').convert('RGBA'))
a[(a[:,:,:3]==(7,24,51)).all(2),:3]=(13,35,71)
o=(11,10,20);s=(83,103,135)
a[8:344,259,:3]=o;a[8:344,260:263,:3]=s;a[8:344,263,:3]=o
a[347,8:256,:3]=o;a[348:351,8:256,:3]=s;a[351,8:256,:3]=o
c1=Image.fromarray(a,'RGBA');save('window_body',c1)
shutil.copyfile(D.parent/'v001/art_frame.png',D/'art_frame.png');c2=Image.open(D/'art_frame.png');save('art_frame',c2)
cs=c1.copy();cs.alpha_composite(c2,(6,26));save('custom_sample',cs)
slot=normalize((56,200,275,510),(44,56),G,8,G[0]);save('slot',slot)
ok1=recolor(slot,G,GOLD);ok2=recolor(slot,G,[GOLD[0],GOLD[1],GOLD[3],GOLD[4],GOLD[3]])
save('ok',row([ok1,ok2]))
# C4: exact 12px native L silhouette from generated TL corner, mirrored to four corners; two-tone blink preserves shape.
corner=quant(R.crop((334,201,423,294)).resize((12,12),Image.Resampling.NEAREST),GOLD)
# Keep the L void empty: source noise below threshold already removed.
co=[corner,corner.transpose(Image.Transpose.FLIP_LEFT_RIGHT),corner.transpose(Image.Transpose.FLIP_TOP_BOTTOM),corner.transpose(Image.Transpose.ROTATE_180)]
co2=[recolor(i,GOLD,[GOLD[0],GOLD[1],GOLD[3],GOLD[4],GOLD[3]]) for i in co]
save('cursor',row(co+co2))
for n,i,j in zip(['tl','tr','bl','br'],co,co2):save('cursor_'+n,row([i,j]))
tab=normalize((907,281,1458,418),(152,28),G,8,G[0]);save('chosen_tab',tab)
pa=normalize((1513,237,2127,442),(168,52),MAG,10,MAG[1]);pa2=recolor(pa,MAG,[MAG[0],MAG[1],MAG[2],MAG[3],MAG[5],MAG[6],MAG[7],MAG[6]])
save('pa_preview',row([pa,pa2]))
# Deterministic preview of C3 at normal and ball widths, type recoloring, C6/C7 stretch seams.
def stretch(im,w,h,k):
 out=Image.new('RGBA',(w,h));sw,sh=im.size
 for xx0,xx1,dx0,dx1 in [(0,k,0,k),(k,sw-k,k,w-k),(sw-k,sw,w-k,w)]:
  for yy0,yy1,dy0,dy1 in [(0,k,0,k),(k,sh-k,k,h-k),(sh-k,sh,h-k,h)]:
   out.paste(im.crop((xx0,yy0,xx1,yy1)).resize((dx1-dx0,dy1-dy0),Image.Resampling.NEAREST),(dx0,dy0))
 return out
save('stretch_checks',row([slot,stretch(slot,92,56,8),stretch(tab,220,28,8),stretch(pa,220,52,10)]))
rampfile=D.parents[1]/'ASSET-006/v002/type_ramps.json'
ramps=json.loads(rampfile.read_text())
colored=[recolor(slot,G,ramps['ramps'][t]) for t in ['Fire','Water','Grass']]
save('slot_type_checks',row(colored+[stretch(colored[0],92,56,8)]))
layout=Image.new('RGBA',(528,352),(4,12,28,255));layout.alpha_composite(cs,(0,0))
for yrow in [196,260]:
 for j in range(5):layout.alpha_composite(colored[j%3],(7+j*50,yrow))
# Selected first slot: brackets 4px outside the slot in the intended relative positions.
for corn,xy in zip(co,[(3,192),(43,192),(3,244),(43,244)]):layout.alpha_composite(corn,xy)
for j in range(3):layout.alpha_composite(recolor(tab,G,ramps['ramps'][['Fire','Water','Grass'][j]]),(264,28+j*36))
layout.alpha_composite(pa,(264,140));save('layout_review',layout)
(D/'processing.json').write_text(json.dumps({'raw':'raw/custom_parts_generated.png','raw_dimensions':list(R.size),'source_crops':{'slot':[56,200,275,510],'cursor_TL':[334,201,423,294],'chosen_tab':[907,281,1458,418],'pa_preview':[1513,237,2127,442]},'operations':['nearest-neighbor native resize','alpha threshold128','nearest RGB palette quantization','corner preservation and uniform middle edge reflow','flat plain interior replacement','exact index recolor for variants and blink','8px transparent animation gaps'],'palettes':{'greys':G,'gold':GOLD,'magenta':MAG},'C1_optional_fill_adopted':'#0d2347','C2':'byte-identical to v001','scale':1,'raw_exact_integer_multiple':False,'preview_scales':[4,0.5],'layout_preview':'Illustrative arrangement only; no engine rendering or text test'},indent=2)+'\n')
# All-parts visual overview, rows separated by 8px transparent gutters.
rows=[row([slot,ok1,ok2]+co+co2),tab,row([pa,pa2])]
ov=Image.new('RGBA',(max(i.width for i in rows),sum(i.height for i in rows)+16));y=0
for r in rows:ov.paste(r,(0,y));y+=r.height+8
save('parts_review',ov)
manifest={'C1':{'file':'window_body.png','cell':[264,352]},'C2':{'file':'art_frame.png','cell':[252,120],'aperture':[4,4,244,112]},'C3':{'file':'slot.png','cell':[44,56],'slices':8},'C4':{'file':'cursor.png','cell':[12,12],'order':['TL1','TR1','BL1','BR1','TL2','TR2','BL2','BR2'],'holds':[8,8],'loop':True},'C5':{'file':'ok.png','cell':[44,56],'frames':2,'holds':[16,16],'loop':True},'C6':{'file':'chosen_tab.png','cell':[152,28],'slices':8},'C7':{'file':'pa_preview.png','cell':[168,52],'frames':2,'holds':[4,4],'loop':True,'slices':10},'gap':8}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
records={}
for name in ['window_body','art_frame','slot','ok','cursor','chosen_tab','pa_preview']:
 path=D/(name+'.png');im=Image.open(path);im.load(); ar=np.array(im);colors=set(map(tuple,ar[ar[:,:,3]>0,:3]));alpha=set(np.unique(ar[:,:,3]).tolist());assert alpha<={0,255}
 if name in ['slot','chosen_tab']:assert colors<=set(map(tuple,rgb(G)))
 records[name]={'size':list(im.size),'colors':len(colors),'alpha':sorted(alpha),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
for name,size in {'window_body':(264,352),'art_frame':(252,120),'slot':(44,56),'ok':(96,56),'cursor':(152,12),'chosen_tab':(152,28),'pa_preview':(344,52)}.items():
 assert Image.open(D/(name+'.png')).size==size
combined_colors=set()
for name in ['window_body','art_frame']:
 ar=np.array(Image.open(D/(name+'.png')));combined_colors|=set(map(tuple,ar[ar[:,:,3]>0,:3]))
assert len(combined_colors)<=16
assert np.all(np.array(c2)[4:116,4:248,3]==0)
assert np.all(a[:,:,3]==255)
assert np.all(a[16:330,259:264,:3]==np.array([o,s,s,s,o])[None,:,:])
assert np.all(a[347:352,16:248,:3]==np.array([o,s,s,s,o])[:,None,:])
assert (D/'art_frame.png').read_bytes()==(D.parent/'v001/art_frame.png').read_bytes()
for im,n,k in [(slot,'C3',8),(tab,'C6',8),(pa,'C7',10)]:
 ar=np.array(im);w,h=im.size;assert np.all(ar[:k,k:w-k]==ar[:k,k:k+1]);assert np.all(ar[h-k:,k:w-k]==ar[h-k:,k:k+1]);assert np.all(ar[k:h-k,:k]==ar[k:k+1,:k]);assert np.all(ar[k:h-k,w-k:]==ar[k:k+1,w-k:]);assert len(set(map(tuple,ar[k:h-k,k:w-k].reshape(-1,4))))==1
for ims in [[ok1,ok2],[pa,pa2]] + [[i,j] for i,j in zip(co,co2)]:
 for i in ims[1:]:assert np.array_equal(np.array(ims[0])[:,:,3],np.array(i)[:,:,3])
for im,w,n in [(Image.open(D/'cursor.png'),12,8),(Image.open(D/'ok.png'),44,2),(Image.open(D/'pa_preview.png'),168,2)]:
 ar=np.array(im)
 for j in range(n-1):assert np.all(ar[:,j*(w+8)+w:(j+1)*(w+8),3]==0)
records['checks']={'dimensions':True,'binary_alpha':True,'C1_edge_fix':True,'C2_byte_identical':True,'five_grey_membership':True,'uniform_9slice_edges':True,'frame_alpha_geometry':True,'clear_8px_gaps':True,'in_game':False}
(D/'validation.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))
