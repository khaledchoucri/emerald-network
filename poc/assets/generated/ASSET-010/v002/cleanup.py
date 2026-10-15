"""Reproduce original generated strike VFX from raw/*.png. Pillow, NumPy, SciPy.
Run from any directory: python <path>/cleanup.py
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parent
GRAY = np.array([32, 88, 144, 200, 255])
CONFIG = {
    'slash': {'cell': [76,142], 'drawn':4, 'holds':[4,4,3,3], 'anchor':[38,71], 'pad':12},
    'stab': {'cell':[62,26], 'drawn':2, 'holds':[3,2], 'anchor':[4,13], 'pad':3},
    'slash_arc': {'cell':[142,176], 'drawn':3, 'holds':[1,3,3,3,1], 'anchor':[71,88], 'pad':12, 'blank_ends':True},
    'claw': {'cell':[84,204], 'drawn':3, 'holds':[1,3,3,3,1], 'anchor':[42,102], 'pad':7, 'blank_ends':True},
    'jaws': {'cell':[64,96], 'drawn':5, 'holds':[3,3,2,6,6], 'anchor':[32,48], 'pad':6},
}
records = {}
all_frames = {}

def cleaned(raw, limit=None):
    a = np.asarray(raw.convert('RGBA')).copy()
    mask = a[:,:,3] >= 192
    labs, _ = label(mask, structure=np.ones((3,3)))
    counts = np.bincount(labs.ravel())
    keep = np.where(counts >= max(8, mask.sum() * .00025))[0]
    keep = keep[keep != 0]
    if limit is not None:
        keep = np.argsort(counts[1:])[::-1][:limit]+1
    mask &= np.isin(labs, keep)
    a[~mask] = 0
    a[mask,3] = 255
    return Image.fromarray(a)

for name,cfg in CONFIG.items():
    raw = Image.open(ROOT / 'raw' / f'{name}.png').convert('RGBA')
    n = cfg['drawn']
    parts = []
    bboxes = []
    # Each source was requested as one row; divide the generator canvas into
    # equal columns, then retain the common vertical origin and a shared scale.
    for i in range(n):
        part = raw.crop((round(i*raw.width/n),0,round((i+1)*raw.width/n),raw.height))
        part = cleaned(part, 1 if name=='slash' and i<2 else None)
        parts.append(part)
        bboxes.append(part.getbbox())
    y0 = min(b[1] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    cw,ch = cfg['cell']
    max_width = max(b[2]-b[0] for b in bboxes)
    scale = min((cw-2*cfg['pad'])/max_width, (ch-2*cfg['pad'])/(y1-y0))
    frames = []
    for i,(part,bbox) in enumerate(zip(parts,bboxes)):
        crop = part.crop((bbox[0], y0, bbox[2], y1))
        target = (max(1,round(crop.width*scale)),max(1,round(crop.height*scale)))
        resized = crop.resize(target, Image.Resampling.NEAREST)
        frame = Image.new('RGBA',(cw,ch))
        frame.paste(resized, ((cw-target[0])//2, (ch-target[1])//2))
        frames.append(frame)
    if name=='slash':
        # The four-frame generator repeated the rejected checkered first core.
        # Replace only frame1 with independently generated solid stroke art.
        first = cleaned(Image.open(ROOT/'raw/slash_first.png'),1)
        first = first.crop(first.getbbox())
        h = frames[1].getbbox()[3]-frames[1].getbbox()[1]
        factor = h/first.height
        target = (round(first.width*factor),h)
        first = first.resize(target, Image.Resampling.NEAREST)
        frames[0] = Image.new('RGBA',(cw,ch))
        frames[0].paste(first,((cw-target[0])//2,(ch-target[1])//2))
    if cfg.get('blank_ends'):
        frames = [Image.new('RGBA',(cw,ch))]+frames+[Image.new('RGBA',(cw,ch))]
    if name=='stab':
        # The generator put the dominant luminous flash at the left base.
        # Mirror cells so that flash is the rightward tip and shaft trails left.
        frames = [ImageOps.mirror(f) for f in frames]
    for i,frame in enumerate(frames):
        a = np.asarray(frame).copy()
        valid = a[:,:,3] >= 192
        lum = a[:,:,:3].astype(float).mean(2)
        snapped = GRAY[np.abs(lum[:,:,None]-GRAY).argmin(2)]
        for c in range(3):a[:,:,c] = np.where(valid,snapped,0)
        a[:,:,3] = np.where(valid,255,0)
        if name=='jaws' and i==4:
            # Fade via remaining geometry and dimmer opaque shades, not alpha.
            a[:,:,:3] = np.minimum(a[:,:,:3],144)
        if name=='slash' and i==0:
            # Repair native resampling dropouts in the generated thin core:
            # make its interior 2px solid white, preserving the generated
            # row-centre staircase and outer silhouette, tapering only at tips.
            rows=np.flatnonzero(valid.any(1))
            for y in rows[2:-2]:
                xs=np.flatnonzero(valid[y]); mid=round(float(xs.mean()))
                for x in [mid-1,mid]:
                    if valid[y,x]: a[y,x]=[255,255,255,255]
        frames[i] = Image.fromarray(a)
    width = len(frames)*cw+(len(frames)-1)*8
    sheet = Image.new('RGBA',(width,ch))
    for i,f in enumerate(frames):sheet.paste(f,(i*(cw+8),0))
    sheet.save(ROOT/f'{name}.png')
    sheet.resize((width*4,ch*4),Image.Resampling.NEAREST).save(ROOT/f'{name}_review_4x.png')
    sheet.resize((width//2,ch//2),Image.Resampling.NEAREST).save(ROOT/f'{name}_review_half.png')
    # Diagnostic loops show holds at slowed 5x timing. They are not game tests.
    diagnostic=[]
    for f in frames:
        bg=Image.new('RGBA',f.size,(20,28,44,255)); bg.alpha_composite(f)
        diagnostic.append(bg.convert('RGB').resize((cw*4,ch*4),Image.Resampling.NEAREST))
    diagnostic.append(Image.new('RGB',(cw*4,ch*4),(20,28,44)))
    diagnostic[0].save(ROOT/f'{name}_playback_slow.gif',save_all=True,append_images=diagnostic[1:],
        duration=[round(h*1000/60*5) for h in cfg['holds']]+[500],loop=0,disposal=2)
    pixels=np.asarray(sheet)
    palette=sorted({tuple(p) for p in pixels[pixels[:,:,3]==255,:3].tolist()})
    assert all(p in [(g,g,g) for g in GRAY] for p in palette)
    assert set(np.unique(pixels[:,:,3])) == {0,255}
    for i in range(len(frames)-1):assert not pixels[:,(i+1)*cw+i*8:(i+1)*(cw+8),3].any()
    assert not pixels[0,:,3].any() and not pixels[-1,:,3].any()
    assert not pixels[:,0,3].any() and not pixels[:,-1,3].any()
    checks={'dimensions':list(sheet.size),'frames':len(frames),'cell':[cw,ch],'gap':8,
        'holds_game_frames':cfg['holds'],'total_game_frames':sum(cfg['holds']),
        'suggested_anchor':cfg['anchor'],'alpha_values':[0,255], 'palette':palette,
        'source_dimensions':list(raw.size),'isotropic_scale':scale,'source_frame_bboxes':bboxes,
        'sha256':hashlib.sha256((ROOT/f'{name}.png').read_bytes()).hexdigest()}
    records[name]=checks
    all_frames[name]=frames

# Static tint review uses the currently approved v002 ramps, not older v001.
ramps_path = ROOT.parents[1]/'ASSET-006/v002/type_ramps.json'
ramps=json.loads(ramps_path.read_text())['ramps']
types=['Normal','Grass','Dark','Steel']
review=Image.new('RGBA',(680,560),(20,28,44,255))
draw=ImageDraw.Draw(review)
for row,typename in enumerate(types):
    draw.text((8,row*140+4),typename,fill='white')
    for col,(name,frames) in enumerate(all_frames.items()):
        f=frames[2] if name in ('jaws','slash_arc','claw') else frames[min(1,len(frames)-1)]
        a=np.asarray(f).copy(); mask=a[:,:,3]==255
        original=a[:,:,0].copy()
        for g,color in zip(GRAY,ramps[typename]):
            where=mask & (original==g)
            # Use original frame intensity for indexing; tint once per pixel.
            rgb=tuple(int(color[j:j+2],16) for j in (1,3,5))
            a[where,:3]=rgb
        tile=Image.fromarray(a)
        review.alpha_composite(tile,(col*134+12,row*140+20)) if tile.height<=120 else review.alpha_composite(tile.resize((tile.width//2,tile.height//2),Image.Resampling.NEAREST),(col*134+12,row*140+20))
        draw.text((col*134+8,row*140+124),name,fill='white')
review.save(ROOT/'tint_review.png')
(ROOT/'processing.json').write_text(json.dumps({'effects':records,'alpha_threshold':192,
    'cleanup':'connected-component dust removal; aspect-preserving common scale; nearest neighbor; five-gray snap; SLASH first generated separately and resampling core repaired; STAB cells mirrored so dominant flash leads right',
    'runtime_verified':False,'tint_reference':str(ramps_path.relative_to(ROOT.parents[3])),
    'diagnostic_gif':'5x slower than requested holds, repeated with final pause; not engine playback'},indent=2)+'\n')
(ROOT/'validation.json').write_text(json.dumps({'effects':records,'checks_passed':[
    'complete PNG decode','native dimensions','binary alpha','palette subset of exactly five specified gray slots',
    '8px transparent gutters','empty outer edge'], 'unchecked':['renderer anchors','60fps game playback','integration tint rendering']},indent=2)+'\n')
print(json.dumps({name:r['dimensions'] for name,r in records.items()}))
