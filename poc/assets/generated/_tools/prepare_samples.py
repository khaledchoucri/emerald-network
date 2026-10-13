#!/usr/bin/env python3
"""Native asset cleanup. Explicit config crops; never changes source files.

python cleanup.py config.json
Modes: backdrop, hit, hud, card. See example_config.json for the schema.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

GREYS = ['#202020', '#585858', '#909090', '#c8c8c8', '#ffffff']


def rgb(hex_string):
    return tuple(bytes.fromhex(hex_string.lstrip('#')))


def components(mask):
    """4-connected foreground; disconnected square sparks remain independently visible."""
    seen = np.zeros(mask.shape, dtype=bool)
    result = []
    for yy, xx in zip(*np.where(mask)):
        if seen[yy, xx]:
            continue
        seen[yy, xx] = True
        stack, points = [(yy, xx)], []
        while stack:
            y, x = stack.pop()
            points.append((y, x))
            for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx] = True
                    stack.append((ny,nx))
        result.append(points)
    return result


def source_cell(item, cfg, log):
    with Image.open(item['input']) as source:
        source.load()
        img = source.convert('RGBA')
    box = item.get('crop', [0, 0, img.width, img.height])
    if len(box) != 4 or not (0 <= box[0] < box[2] <= img.width and 0 <= box[1] < box[3] <= img.height):
        raise ValueError(f'Invalid crop {box} for {img.size}')
    img = img.crop(tuple(box))
    arr = np.asarray(img).copy()
    threshold = item.get('alpha_threshold', cfg.get('alpha_threshold', 128))
    original_partial = int(np.sum((arr[:,:,3] > 0) & (arr[:,:,3] < 255)))
    arr[:,:,3] = np.where(arr[:,:,3] >= threshold, 255, 0)
    # Explicit chroma-key only if requested. Never guess an opaque backdrop is alpha.
    if 'chroma_key' in item:
        key = np.array(rgb(item['chroma_key']), dtype=int)
        distance = np.max(np.abs(arr[:,:,:3].astype(int)-key), axis=2)
        arr[distance <= item.get('chroma_tolerance', 0),3] = 0
    minimum = item.get('minimum_component_pixels', cfg.get('minimum_component_pixels', 1))
    removed = 0
    if minimum > 1:
        for pts in components(arr[:,:,3] == 255):
            if len(pts) < minimum:
                ys, xs = zip(*pts)
                arr[ys,xs,3] = 0
                removed += len(pts)
    arr[arr[:,:,3] == 0,:3] = 0
    img = Image.fromarray(arr)
    if item.get('trim_alpha', False):
        bbox = img.getbbox()
        if bbox is None:
            raise ValueError('Empty artwork after alpha cleanup')
        img = img.crop(bbox)
    log.append({'input': item['input'], 'crop': box, 'source_size_after_crop': list(img.size),
                'alpha_threshold': threshold, 'partial_alpha_pixels_thresholded': original_partial,
                'component_minimum_source_pixels': minimum, 'removed_component_pixels': removed,
                'trim_alpha': item.get('trim_alpha', False)})
    return img


def fit(img, size, log, margin=0, opaque=None):
    available = (size[0]-2*margin, size[1]-2*margin)
    scale = min(available[0]/img.width, available[1]/img.height)
    new = (max(1, round(img.width*scale)), max(1, round(img.height*scale)))
    # Roundoff differs by less than one native pixel. No anisotropic stretching.
    canvas = Image.new('RGBA', tuple(size), (*opaque,255) if opaque else (0,0,0,0))
    resized = img.resize(new, Image.Resampling.NEAREST)
    position = ((size[0]-new[0])//2, (size[1]-new[1])//2)
    canvas.alpha_composite(resized, position)
    log.append({'operation': 'aspect_preserving_fit', 'original': list(img.size), 'native': list(size),
                'scale': scale, 'resized': list(new), 'offset': list(position), 'resampler': 'nearest'})
    return canvas


def fixed_palette(img, colors):
    arr = np.asarray(img).copy()
    palette = np.array([rgb(c) for c in colors], dtype=np.int32)
    flat = arr[:,:,:3].astype(np.int32)
    distance = ((flat[:,:,None,:]-palette[None,None,:,:])**2).sum(axis=3)
    indexes = distance.argmin(axis=2)
    arr[:,:,:3] = palette[indexes]
    arr[arr[:,:,3] == 0,:3] = 0
    return Image.fromarray(arr), indexes


def quantize(img, maximum=16):
    # Quantize visible pixels only; alpha-0 must not consume a palette slot.
    arr = np.asarray(img).copy()
    visible = arr[:,:,3] == 255
    if not np.any(visible):
        raise ValueError('Empty image')
    strip = Image.fromarray(arr[:,:,:3][visible][None,:,:])
    reduced = strip.quantize(colors=maximum, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE).convert('RGB')
    arr[:,:,:3][visible] = np.asarray(reduced)[0]
    arr[~visible,:3] = 0
    return Image.fromarray(arr)


def pack(images, gap=8):
    w, h = images[0].size
    if not all(i.size == (w,h) for i in images):
        raise ValueError('All frames need equal native cell sizes')
    sheet = Image.new('RGBA', (w*len(images)+gap*(len(images)-1),h))
    for index,img in enumerate(images):
        sheet.paste(img,(index*(w+gap),0))
    return sheet


def report_image(path, expected, max_colors=16, opaque=False, palette=None, cells=None, gap=8):
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(image.convert('RGBA'))
        size = image.size
    visible = arr[:,:,3] == 255
    colors = sorted(set(tuple(int(c) for c in pixel) for pixel in arr[:,:,:3][visible]))
    check = {'dimensions': size == tuple(expected), 'binary_alpha': set(np.unique(arr[:,:,3])) <= {0,255},
             'palette_limit': len(colors) <= max_colors, 'nonempty': bool(visible.any())}
    if opaque:
        check['fully_opaque'] = bool(visible.all())
    if palette:
        check['palette_membership'] = set(colors) <= set(rgb(c) for c in palette)
    if cells:
        width, count = cells
        check['clear_frame_gaps'] = all(not np.any(arr[:,n*(width+gap)+width:(n+1)*(width+gap),3])
                                        for n in range(count-1))
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'dimensions': list(size), 'visible_colors': ['#%02x%02x%02x' % c for c in colors],
            'checks': {k:bool(v) for k,v in check.items()}, 'passed': all(check.values())}


def save(img, out, expected, results, **checks):
    img.save(out)
    results.append(report_image(out, expected, **checks))


def uniform_nineslice(img, corner):
    """Keep corner artwork, repeat middle-edge samples, flatten inside for 9-slice."""
    arr = np.asarray(img).copy()
    h,w = arr.shape[:2]
    original = arr.copy()
    arr[:corner,corner:w-corner] = original[:corner,w//2:w//2+1]
    arr[h-corner:,corner:w-corner] = original[h-corner:,w//2:w//2+1]
    arr[corner:h-corner,:corner] = original[h//2:h//2+1,:corner]
    arr[corner:h-corner,w-corner:] = original[h//2:h//2+1,w-corner:]
    arr[corner:h-corner,corner:w-corner] = original[h//2,w//2]
    return Image.fromarray(arr)


def nineslice_checks(img,corner=8):
    arr=np.asarray(img)
    h,w=arr.shape[:2]
    return {
        'uniform_top_edge':bool(np.all(arr[:corner,corner:w-corner]==arr[:corner,w//2:w//2+1])),
        'uniform_bottom_edge':bool(np.all(arr[h-corner:,corner:w-corner]==arr[h-corner:,w//2:w//2+1])),
        'uniform_left_edge':bool(np.all(arr[corner:h-corner,:corner]==arr[h//2:h//2+1,:corner])),
        'uniform_right_edge':bool(np.all(arr[corner:h-corner,w-corner:]==arr[h//2:h//2+1,w-corner:])),
        'uniform_center_fill':bool(np.all(arr[corner:h-corner,corner:w-corner]==arr[h//2,w//2]))}


def reflow_nineslice(raw, source_corner, native=(96,34), corner=8):
    """Repack source corner/edge/fill patches instead of shrinking a wide box."""
    w,h=raw.size
    c=source_corner
    nw,nh=native
    image=Image.new('RGBA',native)
    for sx,sy,dx,dy in ((0,0,0,0),(w-c,0,nw-corner,0),
                       (0,h-c,0,nh-corner),(w-c,h-c,nw-corner,nh-corner)):
        image.paste(raw.crop((sx,sy,sx+c,sy+c)).resize((corner,corner),Image.Resampling.NEAREST),(dx,dy))
    for box,size,pos in (((w//2,0,w//2+1,c),(nw-2*corner,corner),(corner,0)),
                         ((w//2,h-c,w//2+1,h),(nw-2*corner,corner),(corner,nh-corner)),
                         ((0,h//2,c,h//2+1),(corner,nh-2*corner),(0,corner)),
                         ((w-c,h//2,w,h//2+1),(corner,nh-2*corner),(nw-corner,corner))):
        image.paste(raw.crop(box).resize(size,Image.Resampling.NEAREST),pos)
    image.paste(raw.getpixel((w//2,h//2)),(corner,corner,nw-corner,nh-corner))
    return image


def stretch_nineslice(img,size,corner=8):
    return reflow_nineslice(img,corner,tuple(size),corner)


def run(cfg):
    outdir = Path(cfg['output_dir'])
    outdir.mkdir(parents=True, exist_ok=True)
    ops, results = [], []
    mode = cfg['mode']
    if mode == 'backdrop':
        raw = source_cell(cfg['items'][0],cfg,ops)
        img = fit(raw,(528,352),ops,opaque=rgb(cfg.get('padding_color','#061833')))
        if cfg.get('palette'):
            img,_=fixed_palette(img,cfg['palette'])
            ops.append({'operation':'nearest_fixed_palette','palette':cfg['palette'],'dither':False})
        else:
            img = quantize(img,16)
            ops.append({'operation':'visible_RGB_median_cut','maximum_colors':16,'dither':False})
        if cfg.get('sky_bands'):
            arr=np.asarray(img).copy()
            before=arr.copy()
            source_horizon=cfg['source_horizon']
            target_horizon=cfg['target_horizon']
            shift=target_horizon-source_horizon
            if shift<0:
                raise ValueError('Backdrop helper only supports positive grid translation')
            arr[target_horizon:]=before[source_horizon:352-shift]
            for start,end,color in cfg['sky_bands']:
                arr[start:end,:,:3]=rgb(color)
                arr[start:end,:,3]=255
            img=Image.fromarray(arr)
            ops.append({'operation':'translate_grid_and_flatten_sky',
                        'source_horizon_y':source_horizon,'target_horizon_y':target_horizon,
                        'grid_translation_y':shift,'bottom_overflow_crop_pixels':shift,
                        'sky_bands':cfg['sky_bands'],'grid_floor_resized':False})
        if cfg.get('flatten_floor_dark'):
            arr=np.asarray(img).copy()
            start=cfg.get('target_horizon',150)
            threshold=cfg.get('floor_grid_blue_threshold',100)
            floor=arr[start:,:,:3]
            mask=floor[:,:,2]<threshold
            floor[mask]=rgb(cfg['flatten_floor_dark'])
            img=Image.fromarray(arr)
            ops.append({'operation':'flatten_floor_nongrid_darktones','start_y':start,
                        'grid_keep_blue_channel_at_least':threshold,
                        'replacement':cfg['flatten_floor_dark'],'pixels_flattened':int(mask.sum())})
        save(img,outdir/'backdrop.png',(528,352),results,opaque=True)
    elif mode == 'hit':
        if len(cfg['items']) != 6:
            raise ValueError('HIT requires exactly six explicit crops')
        frames = []
        sources=[source_cell(item,cfg,ops) for item in cfg['items']]
        common_scale = min(60/max(i.width for i in sources),60/max(i.height for i in sources))
        for source in sources:
            if cfg.get('common_scale'):
                size=(max(1,round(source.width*common_scale)),max(1,round(source.height*common_scale)))
                frame=Image.new('RGBA',(64,64))
                offset=((64-size[0])//2,(64-size[1])//2)
                frame.paste(source.resize(size,Image.Resampling.NEAREST),offset)
                ops.append({'operation':'common_scale_centered_frame','scale':common_scale,
                            'original':list(source.size),'resized':list(size),'offset':list(offset)})
            else:
                frame = fit(source,(64,64),ops,margin=cfg.get('margin',0))
            if cfg.get('gray_thresholds'):
                arr=np.asarray(frame).copy()
                gray=np.rint(arr[:,:,:3].mean(axis=2))
                tone=np.digitize(gray,cfg['gray_thresholds'])
                arr[:,:,:3]=np.array([rgb(c) for c in GREYS],dtype=np.uint8)[tone]
                arr[arr[:,:,3]==0,:3]=0
                frame=Image.fromarray(arr)
            else:
                frame,_ = fixed_palette(frame,GREYS)
            frames.append(frame)
        img = pack(frames)
        save(img,outdir/'hit.png',(424,64),results,palette=GREYS,max_colors=5,cells=(64,6))
        ops.append({'operation':'nearest_grey_palette','palette':GREYS})
        if cfg.get('gray_thresholds'):
            ops.append({'operation':'gray_tone_band_remap','source_thresholds':cfg['gray_thresholds'],
                        'palette':GREYS,'reason':'retain five source material tiers, including dark outline'})
        ops.append({'operation':'pack','cell':[64,64],'frames':6,'gap':8,'anchor':[32,32],
                    'times_game_frames':[1,1,2,2,2,2],'loop':False})
        used = set(results[-1]['visible_colors'])
        results[-1]['checks']['all_five_greys_used'] = used == set(GREYS)
        results[-1]['passed'] = all(results[-1]['checks'].values())
    elif mode == 'hud':
        raw=source_cell(cfg['items'][0],cfg,ops)
        if cfg.get('source_corner'):
            base=reflow_nineslice(raw,cfg['source_corner'])
            ops.append({'operation':'reflow_generated_9slice','source_corner_square':cfg['source_corner'],
                        'native_corner':[8,8],'native_size':[96,34],
                        'detail':'uniform middle edge samples;flatcenter;preservedcornerpatches'})
        else:
            base = fit(raw,(96,34),ops)
        base = uniform_nineslice(base,8)
        ops.append({'operation':'normalize_nineslice','corner':[8,8],
                    'detail':'keep corners; repeat central edge samples; flatten central fill'})
        # Index the ONE base, then substitute palette: geometry stays pixel-identical.
        base,indexes = fixed_palette(base,cfg['base_palette'])
        alpha = np.asarray(base)[:,:,3]
        frames=[]
        for name,palette in cfg['colorways'].items():
            if len(palette) != len(cfg['base_palette']):
                raise ValueError('All HUD palettes must have the same index count')
            arr = np.zeros((34,96,4),dtype=np.uint8)
            arr[:,:,:3] = np.array([rgb(c) for c in palette],dtype=np.uint8)[indexes]
            arr[:,:,3] = alpha
            arr[alpha==0,:3] = 0
            img = Image.fromarray(arr)
            frames.append(img)
            save(img,outdir/(name+'.png'),(96,34),results)
            results[-1]['checks'].update(nineslice_checks(img))
            results[-1]['passed']=all(results[-1]['checks'].values())
        save(pack(frames),outdir/'h1_colorways.png',(96*len(frames)+8*(len(frames)-1),34),results,
             max_colors=16*len(frames),cells=(96,len(frames)))
        # Colorway equality is measured on index geometry, not RGB identity.
        results[-1]['checks']['identical_alpha_geometry'] = all(
            np.array_equal(np.asarray(i)[:,:,3],alpha) for i in frames)
        geometry_equal=True
        for img,palette in zip(frames,cfg['colorways'].values()):
            if len(set(palette)) != len(palette):
                geometry_equal=False
                break
            variant=np.asarray(img)
            recovered=np.zeros((34,96),dtype=np.uint8)
            for n,color in enumerate(palette):
                recovered[np.all(variant[:,:,:3]==rgb(color),axis=2)]=n
            geometry_equal &= bool(np.array_equal(recovered[alpha==255],indexes[alpha==255]))
        results[-1]['checks']['identical_material_geometry']=geometry_equal
        results[-1]['passed'] = all(results[-1]['checks'].values())
        frame_names=list(cfg['colorways'])
        synchro=[frames[frame_names.index(n)] for n in ('synchro1','synchro2')]
        save(pack(synchro),outdir/'synchro.png',(200,34),results,max_colors=16,cells=(96,2))
        player=frames[frame_names.index('player')]
        foe=frames[frame_names.index('foe')]
        stretches=[stretch_nineslice(player,(44,24)),stretch_nineslice(player,(200,34)),
                   stretch_nineslice(foe,(60,34))]
        preview=Image.new('RGBA',(320,34))
        x=0
        for stretched in stretches:
            preview.paste(stretched,(x,0));x+=stretched.width+8
        save(preview,outdir/'h1_stretch_preview.png',(320,34),results,max_colors=12)
        results[-1]['checks']['preserved_8x8_corners']=all(
            np.array_equal(np.asarray(stretched)[y:y+8,x:x+8],np.asarray(original)[oy:oy+8,ox:ox+8])
            for stretched,original in zip(stretches,[player,player,foe])
            for x,y,ox,oy in ((0,0,0,0),(stretched.width-8,0,original.width-8,0),
                              (0,stretched.height-8,0,original.height-8),
                              (stretched.width-8,stretched.height-8,original.width-8,original.height-8)))
        results[-1]['checks']['stretch_uniform_edges_fill']=all(all(nineslice_checks(i).values()) for i in stretches)
        results[-1]['passed']=all(results[-1]['checks'].values())
        ops.append({'operation':'9slice_stretch_preview','sizes':[[44,24],[200,34],[60,34]],
                    'colorways':['player','player','foe'],'corner':[8,8],'gap':8,'review_only':True})
        ops.append({'operation':'recolor_single_indexed_base','base_palette':cfg['base_palette'],
                    'colorways':cfg['colorways'],'corner':[8,8],
                    'synchro_timing_game_frames':[8,8],'loop':True})
    elif mode == 'ramps':
        data = json.loads(Path(cfg['ramps_json']).read_text())
        order, ramps = data['type_order'], data['ramps']
        if len(order) != 17 or any(len(ramps[t]) != 5 for t in order):
            raise ValueError('Ramp format must be 17 types × 5 tones')
        image = Image.new('RGBA',(80,272))
        luminances = {}
        for row,name in enumerate(order):
            values=[]
            for col,color in enumerate(ramps[name]):
                image.paste((*rgb(color),255),(col*16,row*16,col*16+16,row*16+16))
                srgb=np.array(rgb(color))/255.0
                linear=np.where(srgb<=0.04045,srgb/12.92,((srgb+0.055)/1.055)**2.4)
                values.append(float(linear @ np.array([0.2126,0.7152,0.0722])))
            luminances[name]=values
        save(image,outdir/'type_ramps.png',(80,272),results,max_colors=85,opaque=True)
        results[-1]['checks']['all_ramps_monotonic_luminance'] = all(
            all(a<b for a,b in zip(vals,vals[1:])) for vals in luminances.values())
        results[-1]['checks']['fire_matches_STYLE'] = ramps['Fire'] == [
            '#9d220f','#dc4b24','#fc871f','#fef237','#fefdf2']
        results[-1]['passed']=all(results[-1]['checks'].values())
        ops.append({'operation':'render_17x5_swatch_palette','type_order':order,
                    'swatch_size':[16,16],'relative_luminance':luminances})
        if cfg.get('hit_png'):
            with Image.open(cfg['hit_png']) as source:
                source.load()
                arr=np.asarray(source.convert('RGBA')).copy()
            if arr.shape[:2] != (64,424):
                raise ValueError('Tint test requires native 424×64 HIT atlas')
            visible=arr[:,:,3]==255
            colors=set(map(tuple,arr[:,:,:3][visible]))
            if not colors <= set(rgb(c) for c in GREYS):
                raise ValueError('HIT contains non-ramp gray values')
            indices=np.zeros(arr.shape[:2],dtype=np.uint8)
            for n,color in enumerate(GREYS):
                indices[np.all(arr[:,:,:3]==rgb(color),axis=2)]=n
            tinted=[]
            for name in order:
                copy=arr.copy()
                copy[:,:,:3]=np.array([rgb(c) for c in ramps[name]],dtype=np.uint8)[indices]
                copy[~visible,:3]=0
                tinted.append(Image.fromarray(copy))
            vertical=Image.new('RGBA',(424,17*64+16*8))
            for n,img in enumerate(tinted):
                vertical.paste(img,(0,n*72))
            save(vertical,outdir/'hit_all_types.png',(424,1216),results,max_colors=85)
            peaks=[int(np.sum(arr[:,n*72:n*72+64,3]==255)) for n in range(6)]
            peak_frame=cfg.get('peak_frame',int(np.argmax(peaks)))
            if peak_frame not in range(6):
                raise ValueError('peak_frame must be 0..5')
            previews=[img.crop((peak_frame*72,0,peak_frame*72+64,64)) for img in tinted]
            save(pack(previews),outdir/'hit_types_side_by_side.png',(1216,64),results,
                 max_colors=85,cells=(64,17))
            ops.append({'operation':'exact_indexed_HIT_type_recolor','type_order':order,
                        'source_hit':cfg['hit_png'],'peak_frame':peak_frame,
                        'animation_preview_rows':'one type per row in type_order',
                        'still_preview_columns':'one type per column in type_order',
                        'identical_geometry':all(np.array_equal(np.asarray(i)[:,:,3],arr[:,:,3]) for i in tinted)})
    elif mode == 'card':
        if len(cfg['items']) != 2:
            raise ValueError('Card sample requires front and back only')
        frames=[]
        for item in cfg['items']:
            img = fit(source_cell(item,cfg,ops),(72,88),ops)
            if cfg.get('palette'):
                img,_=fixed_palette(img,cfg['palette'])
                ops.append({'operation':'nearest_fixed_palette','palette':cfg['palette'],'dither':False})
            else:
                img = quantize(img,16)
            if item.get('blank_window',False):
                # Flat existing tone, not transparent: the symbol is rendered over it.
                arr = np.asarray(img).copy()
                arr[16:56,16:56] = arr[36,36]
                tx0,ty0,tx1,ty1=cfg.get('tab_box',[56,72,72,88])
                tab_alpha=arr[ty0:ty1,tx0:tx1,3].copy()
                tab_center=arr[36,36].copy()
                arr[ty0:ty1,tx0:tx1] = tab_center
                if cfg.get('preserve_tab_silhouette',False):
                    arr[ty0:ty1,tx0:tx1,3]=tab_alpha
                    arr[arr[:,:,3]==0,:3]=0
                img = Image.fromarray(arr)
                ops.append({'operation':'flatten_blank_symbol_window_and_code_tab',
                            'window_xyxy':[16,16,56,56],'code_tab_xyxy':[tx0,ty0,tx1,ty1],
                            'tab_assumption':'16×16 interior bottom-right reservation, avoiding outer silhouette'})
            name = item.get('name','front' if not frames else 'back')
            save(img,outdir/('card_'+name+'.png'),(72,88),results)
            if item.get('blank_window',False):
                arr=np.asarray(img)
                results[-1]['checks']['window_40x40_flat'] = bool(np.all(arr[16:56,16:56]==arr[36,36]))
                tab=arr[ty0:ty1,tx0:tx1]
                results[-1]['checks']['tab_16x16_flat_visible_fill'] = bool(np.all(tab[:,:,:3][tab[:,:,3]==255]==tab_center[:3]))
                results[-1]['passed'] = all(results[-1]['checks'].values())
            frames.append(img)
        save(pack(frames),outdir/'card_front_back.png',(152,88),results,max_colors=32,cells=(72,2))
        results[-1]['checks']['shared_front_back_outline_alpha']=bool(np.array_equal(
            np.asarray(frames[0])[:,:,3],np.asarray(frames[1])[:,:,3]))
        results[-1]['passed']=all(results[-1]['checks'].values())
        ops.append({'operation':'pack','cell':[72,88],'frames':['front','back'],'gap':8,
                    'anchor':[36,44],'turning_frames':'not_in_sample'})
    else:
        raise ValueError(f'Unknown mode {mode}')
    for filename in cfg.get('review_names',[]):
        source=outdir/filename
        with Image.open(source) as image:
            scale=4
            review=image.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST)
            maximum=len(set(tuple(p) for p in np.asarray(image.convert('RGBA'))[:,:,:3].reshape(-1,3)))
            destination=outdir/(source.stem+'_review_4x.png')
            save(review,destination,review.size,results,max_colors=maximum)
            results[-1]['review_only']=True
        ops.append({'operation':'integer_review_enlargement','source':filename,'scale':4,
                    'resampler':'nearest','review_only':True})
        if cfg.get('half_reviews'):
            with Image.open(source) as image:
                half=image.resize((image.width//2,image.height//2),Image.Resampling.NEAREST)
                save(half,outdir/(source.stem+'_review_half.png'),half.size,results,max_colors=maximum)
                results[-1]['review_only']=True
            ops.append({'operation':'half_size_review','source':filename,'resampler':'nearest','review_only':True})
    record={'mode':mode,'config':cfg,'operations':ops,'outputs':results,
            'all_checks_passed':all(r['passed'] for r in results),
            'limits':['Visual review and native/half-size readability remain required.',
                      'No in-game, timing playback, or renderer integration validation performed.',
                      'Component filtering is on source pixels; use minimum=1 to preserve intended sparks.',
                      'HUD edge normalization preserves corners but can change source edge detail.',
                      'Center anchors are cell centers, not proof of the artwork focal-point location.']}
    record_path=outdir/cfg.get('record_name','validation.json')
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'validation':str(record_path),'passed':record['all_checks_passed']}))
    return record['all_checks_passed']


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    args=parser.parse_args()
    raise SystemExit(0 if run(json.loads(args.config.read_text())) else 2)
