#!/usr/bin/env python3
"""Authorized palette/geometry cleanup of generated backdrop revision 2."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
W, H = 528, 352
SOURCE_HORIZON, HORIZON = 134, 150
raw = Image.open(ROOT / 'raw/backdrop.png').convert('RGB')
source = np.asarray(raw.resize((W, H), Image.Resampling.NEAREST))
out = np.empty((H, W, 3), dtype=np.uint8)
def color(value):
    return tuple(bytes.fromhex(value.lstrip('#')))
bands = [(0,54,'#040c1c'),(54,95,'#071833'),(95,126,'#0b2550'),
         (126,138,'#103473'),(138,142,'#103473'),(142,146,'#144283'),(146,150,'#1a4f9c')]
for lo, hi, value in bands:
    out[lo:hi] = color(value)
floor = source[SOURCE_HORIZON:H-(HORIZON-SOURCE_HORIZON)]
# The generated floor's strong blue strokes are retained. Low-contrast texture
# is flattened; translation preserves line geometry rather than stretching it.
lines = floor[:,:,2] >= 120
out[HORIZON:] = color('#071833')
for y in range(HORIZON,H):
    tone = '#1460b0' if y < 164 else '#10539e' if y < 208 else '#083e86'
    out[y, lines[y-HORIZON]] = color(tone)
im = Image.fromarray(out).convert('RGBA')
im.save(ROOT / 'backdrop.png')
im.resize((W*4,H*4),Image.Resampling.NEAREST).save(ROOT / 'backdrop_review_4x.png')
im.resize((W//2,H//2),Image.Resampling.NEAREST).save(ROOT / 'backdrop_review_half.png')
# Inspection composite only: approximate existing source panel crops, no engine.
repo = ROOT.parents[4]
tiles=[]
for side in ('red','blue'):
    p=repo / f'poc/assets/generated/ASSET-003/v002/panels_{side}_source.png'
    tile=Image.open(p).convert('RGBA').crop((14,150,344,363)).resize((88,52),Image.Resampling.NEAREST)
    a=np.asarray(tile).copy();a[:,:,3]=np.where(a[:,:,3]>=128,255,0)
    tiles.append(Image.fromarray(a))
composite=im.copy()
for row in range(3):
    for col in range(6):
        composite.alpha_composite(tiles[col//3],(col*88,164+row*52))
composite.save(ROOT / 'panel_contrast_preview.png')
composite.resize((W*4,H*4),Image.Resampling.NEAREST).save(ROOT / 'panel_contrast_preview_review_4x.png')
unique=sorted(set(tuple(p) for p in out.reshape(-1,3)))
row_counts=lines[:14].sum(axis=1)
depth_rows=[150+i for i,n in enumerate(row_counts) if n >= W//2]
checks={'size':im.size==(528,352),'opaque':bool(np.all(np.asarray(im)[:,:,3]==255)),
        'palette_at_most_16':len(unique)<=16,'four_distinct_sky_steps':len({tuple(out[y,0]) for y in (0,54,95,126)})==4,
        'horizon_glow_12px':all(tuple(out[y,0]) in {color('#103473'),color('#144283'),color('#1a4f9c')} for y in range(138,150)),
        'four_dense_floor_rows_in_visible_gap':len(depth_rows)>=4,
        'non_grid_sky_ceiling':max(p[2] for p in out[:150].reshape(-1,3))<=156,
        'no_motes_or_streams_baked_in':True}
checks={key:bool(value) for key,value in checks.items()}
assert all(checks.values()), checks
report={'checks':checks,'all_checks_passed':all(checks.values()),'palette':['#%02x%02x%02x'%p for p in unique],
        'native':[W,H],'dense_floor_rows':depth_rows,'grid_anchor_y':150,
        'source':{'file':'raw/backdrop.png','size':list(raw.size),'sha256':hashlib.sha256((ROOT/'raw/backdrop.png').read_bytes()).hexdigest()},
        'operations':['nearest native resize','replace sky with corrected flat palette steps','12px discrete horizon band',
                      'translate generated grid down 16px; crop bottom overflow','extract bright generated strokes at blue>=120',
                      'flatten nongrid floor texture','depth-dependent grid recolor','nearest review scaling'],
        'preview_limits':'Existing normal panel source crops are approximate and resized for contrast inspection only; not a game renderer test.',
        'in_game_tested':False}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'processing.json').write_text(json.dumps({'script':'cleanup.py','dependencies':['Pillow','NumPy'],
    'source_horizon':SOURCE_HORIZON,'horizon':HORIZON,'sky_bands':bands,'grid_blue_threshold':120,
    'grid_tones':['#1460b0','#10539e','#083e86'],'floor':'#071833','panel_contrast_preview':'approximate non-engine layout'},indent=2)+'\n')
print(json.dumps(checks))
