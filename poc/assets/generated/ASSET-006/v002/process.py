#!/usr/bin/env python3
"""Reproduce native impact deliveries from repository root; Pillow + NumPy.
Shared helpers are imported read-only; v001 sources are never modified.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('base',ROOT/'poc/assets/generated/_tools/prepare_samples.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
OUT=Path(__file__).parent
cfg=json.loads((OUT/'processing.json').read_text())
ops=[];results=[]
for name,job in cfg['effects'].items():
    frames=[]
    sources=[base.source_cell(item,{'alpha_threshold':220,'minimum_component_pixels':48},ops) for item in job['items']]
    w,h=job['cell'];margin=job.get('margin',3)
    scale=min(min((w-2*margin)/s.width,(h-2*margin)/s.height) for s in sources)*job.get('occupancy',1)
    for source in sources:
        new=(max(1,round(source.width*scale)),max(1,round(source.height*scale)))
        native=Image.new('RGBA',(w,h)); art=source.resize(new,Image.Resampling.NEAREST)
        offset=((w-new[0])//2, h-margin-new[1] if job.get('base_aligned') else (h-new[1])//2)
        native.paste(art,offset)
        if job['tintable']:
            arr=np.array(native); gray=np.rint(arr[:,:,:3].mean(axis=2));tones=np.digitize(gray,[95,135,175,225]);arr[:,:,:3]=np.array([base.rgb(c) for c in base.GREYS])[tones];arr[arr[:,:,3]==0,:3]=0;native=Image.fromarray(arr)
        else:
            native,_=base.fixed_palette(native,job['palette'])
        frames.append(native)
        ops.append({'effect':name,'common_scale':scale,'resized':list(new),'offset':list(offset),'source':list(source.size),'nearest':True})
    sheet=base.pack(frames,8)
    output=OUT/(name+'.png');sheet.save(output)
    report=base.report_image(output,[w*len(frames)+8*(len(frames)-1),h],max_colors=5 if job['tintable'] else 16,palette=base.GREYS if job['tintable'] else job['palette'],cells=(w,len(frames)))
    report['checks']['nonempty_frames']=all(np.array(f)[:,:,3].any() for f in frames)
    report['checks']['clear_outer_padding']=all(not(np.array(f)[0,:,3].any() or np.array(f)[-1,:,3].any() or np.array(f)[:,0,3].any() or np.array(f)[:,-1,3].any()) for f in frames)
    report['checks']['frame_count_matches_timing']=len(frames)==len(job['times_game_frames'])
    report['checks']['duration_matches_brief']=sum(job['times_game_frames'])==job['duration']
    report['passed']=all(report['checks'].values());results.append(report)
    sheet.resize((sheet.width*4,h*4),Image.Resampling.NEAREST).save(OUT/(name+'_review_4x.png'))
    sheet.resize((sheet.width//2,h//2),Image.Resampling.NEAREST).save(OUT/(name+'_review_half.png'))
    # Individual cells accompany sheets for anchor/playback examination.
    ops.append({'effect':name,'cell':[w,h],'frames':len(frames),'gap':8,'anchor':job['anchor'],'times_game_frames':job['times_game_frames'],'loop':False,'exact_semantic_anchor_tracking':False})
(OUT/'validation.json').write_text(json.dumps({'passed':all(r['passed'] for r in results),'results':results,'operations':ops},indent=2)+'\n')
assert all(r['passed'] for r in results),results
print(json.dumps({'passed':True,'effects':list(cfg['effects'])}))

# Opaque review board only; the six runtime-candidate sheets remain transparent.
ims=[Image.open(OUT/(n+'.png')).convert('RGBA') for n in cfg['effects']]
board=Image.new('RGBA',(max(i.width for i in ims),sum(i.height+24 for i in ims)),(18,22,34,255))
y=0;draw=ImageDraw.Draw(board)
for name,im in zip(cfg['effects'],ims):
    draw.text((0,y+4),name.upper(),fill='white');board.alpha_composite(im,(0,y+20));y+=im.height+24
board.save(OUT/'effects_native_review.png')
board.resize((board.width*2,board.height*2),Image.Resampling.NEAREST).save(OUT/'effects_review_2x.png')
