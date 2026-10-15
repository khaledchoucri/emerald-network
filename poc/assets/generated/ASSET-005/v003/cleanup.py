#!/usr/bin/env python3
"""Rebuild ASSET-005 B/C at exact native geometry. Run from repository root."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent


def rgb(color):
    return tuple(bytes.fromhex(color.lstrip('#')))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path, expected, cap):
    with Image.open(path) as source:
        source.load()
        arr=np.asarray(source.convert('RGBA'))
        size=source.size
    visible=arr[:,:,3]==255
    colors=sorted(set(map(tuple,arr[:,:,:3][visible])))
    checks={'size':size==tuple(expected),'binary_alpha':set(np.unique(arr[:,:,3]))<={0,255},
            'nonempty':bool(visible.any()),'transparent_RGB_zero':bool(np.all(arr[:,:,:3][~visible]==0)),
            'brightness_cap':all(float(np.dot(c,[.2126,.7152,.0722]))<=float(np.dot(rgb(cap),[.2126,.7152,.0722])) for c in colors)}
    return {'path':path.name,'dimensions':list(size),'sha256':digest(path),
            'visible_colors':['#%02x%02x%02x'%c for c in colors],
            'checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values())}


def preview_image(image,name,records,cap):
    image.save(ROOT/name)
    record=validate(ROOT/name,image.size,cap)
    records.append(record)
    for suffix,scale in (('_review_4x',4),('_review_half',.5)):
        size=(max(1,int(image.width*scale)),max(1,int(image.height*scale)))
        out=ROOT/(Path(name).stem+suffix+'.png')
        image.resize(size,Image.Resampling.NEAREST).save(out)
        item=validate(out,size,cap);item['review_only']=True;records.append(item)


def main():
    config=json.loads((ROOT/'processing.json').read_text())
    records=[]
    operations=[]
    raw=ROOT/config['source']
    source=Image.open(raw).convert('RGBA')
    # Native 6px cells allow one atlas with consistent dimensions for all sizes.
    motes=Image.new('RGBA',(48,34))
    frames=[]
    for row,size in enumerate((2,4,6)):
        phases=[]
        for phase,(body,core) in enumerate(config['mote_colors']):
            cell=Image.new('RGBA',(6,6))
            x=y=(6-size)//2
            cell.paste((*rgb(body),255),(x,y,x+size,y+size))
            cx=cy=x+(size-1)//2
            cell.putpixel((cx,cy),(*rgb(core),255))
            motes.paste(cell,(phase*14,row*14))
            phases.append(cell)
        frames.append(phases)
    preview_image(motes,'motes.png',records,config['core_cap'])
    operations.append({'operation':'exact_square_mote_geometry','sizes':[2,4,6],
                       'native_cell':[6,6],'frames_per_row':4,'rows':3,'gap':8,
                       'lighter_core_pixels':1,'phase_colors':config['mote_colors'],
                       'generation_role':'shape/palette source; reconstructed to exact tiny pixel squares'})

    streams=Image.new('RGBA',(56,120))
    stream_sprites=[]
    for index,item in enumerate(config['streams']):
        crop=source.crop(tuple(item['crop']))
        array=np.asarray(crop)
        alpha=array[:,:,3]>=config['alpha_threshold']
        blue=array[:,:,2].astype(float)
        baseline=np.percentile(blue,20,axis=1)
        alpha &= (blue-baseline[:,None])>=config['minimum_row_contrast']
        alpha &= blue>=config['minimum_source_blue']
        # Derive dash occupancy from source row projection, then snap each dash
        # to an exact width. Removing weak row noise prevents faint ghost dashes.
        occupied=alpha.sum(axis=1)>=max(1,round(alpha.shape[1]*config['row_coverage_minimum']))
        start=None
        for row,on in enumerate(np.r_[occupied,False]):
            if on and start is None:
                start=row
            elif not on and start is not None:
                if row-start<config['minimum_source_dash_rows']:
                    occupied[start:row]=False
                start=None
        nonzero=np.flatnonzero(occupied)
        if len(nonzero)==0:
            raise ValueError('No strong source dashes after halo filtering')
        source_row_trim=[int(nonzero[0]),int(nonzero[-1])+1]
        occupied=occupied[source_row_trim[0]:source_row_trim[1]]
        projected=Image.fromarray(np.where(occupied[:,None],255,0).astype(np.uint8))
        ys=np.asarray(projected.resize((1,item['height']),Image.Resampling.NEAREST))[:,0]>0
        sprite=Image.new('RGBA',(8,120))
        left=(8-item['width'])//2
        for y,on in enumerate(ys):
            if on:
                sprite.paste((*rgb(item['body']),255),(left,y,left+item['width'],y+1))
                sprite.putpixel((left,y),(*rgb(item['edge']),255))
        streams.paste(sprite,(index*16,0))
        stream_sprites.append(sprite)
        operations.append({'operation':'source_dash_row_projection_and_native_snap','index':index,
                           'source_crop':item['crop'],'native_width':item['width'],
                           'native_height':item['height'],'alpha_threshold':config['alpha_threshold'],
                           'row_coverage_minimum':config['row_coverage_minimum'],
                           'source_row_trim':source_row_trim,
                           'minimum_row_contrast':config['minimum_row_contrast'],
                           'minimum_source_dash_rows':config['minimum_source_dash_rows'],
                           'occupied_native_rows':np.flatnonzero(ys).tolist(),
                           'body':item['body'],'edge':item['edge']})
    preview_image(streams,'data_streams.png',records,config['core_cap'])

    ma=np.asarray(motes);sa=np.asarray(streams)
    checks={
        'mote_horizontal_gaps':all(not np.any(ma[:,n*14+6:(n+1)*14,3]) for n in range(3)),
        'mote_vertical_gaps':all(not np.any(ma[n*14+6:(n+1)*14,:,3]) for n in range(2)),
        'stream_gaps':all(not np.any(sa[:,n*16+8:(n+1)*16,3]) for n in range(3)),
        'mote_sizes':all(int(np.sum(ma[row*14:row*14+6,col*14:col*14+6,3]==255))==size*size
                         for row,size in enumerate((2,4,6)) for col in range(4)),
        'stream_dimensions':all(4<=item['width']<=8 and 40<=item['height']<=120 for item in config['streams'])}
    for i,(sprite,item) in enumerate(zip(stream_sprites,config['streams'])):
        box=sprite.getbbox()
        checks[f'stream_{i}_actual_occupied_bounds']=box is not None and box[2]-box[0]==item['width'] and box[3]-box[1]==item['height']
        rows=np.any(np.asarray(sprite)[:,:,3]>0,axis=1)
        checks[f'stream_{i}_multiple_dashes']=int(np.sum(rows & ~np.r_[False,rows[:-1]]))>=3
    for row,size in enumerate((2,4,6)):
        for phase,(_body,core) in enumerate(config['mote_colors']):
            cell=ma[row*14:row*14+6,phase*14:phase*14+6]
            checks[f'mote_{size}_phase_{phase}_one_core']=int(np.sum(np.all(cell[:,:,:3]==rgb(core),axis=2)&(cell[:,:,3]==255)))==1

    backdrop_path=Path(config['approved_backdrop'])
    original_hash=digest(backdrop_path)
    backdrop=Image.open(backdrop_path).convert('RGBA')
    composed=[]
    # 16 frames of 8 game ticks = 128ticks, approx 2.133s. Animation drift is
    # demonstrative only; final scatter, speed and density belong to the engine.
    for tick in range(16):
        image=backdrop.copy()
        for i,(x,y) in enumerate(config['stream_positions']):
            sprite=stream_sprites[i]
            posy=((y-tick*2+120)%240)-120
            layer=Image.new('RGBA',backdrop.size)
            layer.alpha_composite(sprite,(x,posy))
            layer.alpha_composite(sprite,(x,posy+240))
            # Streams remain in sky, never modify backdrop or grid directly.
            layer.paste((0,0,0,0),(0,150,528,352))
            image.alpha_composite(layer)
        for row,x,y,offset in config['mote_positions']:
            phase=(tick+offset)%4
            posy=max(0,min(142,y-tick//4))
            image.alpha_composite(frames[row][phase],(x,posy))
        composed.append(image.convert('RGB'))
    composed[1].save(ROOT/'layered_preview.png')
    composed[1].resize((2112,1408),Image.Resampling.NEAREST).save(ROOT/'layered_preview_review_4x.png')
    composed[1].resize((264,176),Image.Resampling.NEAREST).save(ROOT/'layered_preview_review_half.png')
    # GIF delays have a 10ms resolution; 130/130/140ms repeats approximate the
    # exact 8/60-second source hold. PNG cells and game-tick metadata are exact.
    durations=[130 if i%3!=2 else 140 for i in range(16)]
    composed[0].save(ROOT/'layered_playback.gif',save_all=True,append_images=composed[1:],
                     duration=durations,loop=0,optimize=False,disposal=2)
    with Image.open(ROOT/'layered_playback.gif') as animation:
        checks['preview_has_16_frames']=animation.n_frames==16
        checks['preview_loops']=animation.info.get('loop')==0
        actual_durations=[]
        for frame in range(animation.n_frames):
            animation.seek(frame)
            animation.load()
            actual_durations.append(animation.info.get('duration'))
        checks['preview_delay_roundtrip']=actual_durations==durations
    checks['approved_A_unchanged']=digest(backdrop_path)==original_hash
    record={'brief_revision':2,'delivery':'v003 B/C only','raw':{'path':config['source'],'sha256':digest(raw),'size':list(source.size)},
            'operations':operations,'outputs':records,'sheet_checks':{k:bool(v) for k,v in checks.items()},
            'animation':{'mote_frames':4,'hold_game_frames':8,'fps':60,'loops':True,
                         'stream_sprites_static':True,'preview_frame_count':16,
                         'preview_gif_delay_ms':durations,'preview_gif_sha256':digest(ROOT/'layered_playback.gif'),
                         'preview_engine_motion':'illustrative fixed scatter and drift'},
            'approved_A':{'path':config['approved_backdrop'],'sha256':original_hash},
            'limits':['Layered playback is a preparation preview, not an in-game test.',
                      'Final stream scroll and mote density/speeds remain implementation choices.',
                      'Small 1px cores may alias in half-size nearest-neighbor review.'],
            'all_checks_passed':all(checks.values()) and all(r['passed'] for r in records)}
    (ROOT/'validation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'passed':record['all_checks_passed'],'validation':str(ROOT/'validation.json')}))
    return record['all_checks_passed']


if __name__=='__main__':
    raise SystemExit(0 if main() else 2)
