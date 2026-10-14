"""Reproduce the SLASH source delivery from the retained imagegen PNG.

Run: python poc/assets/generated/ASSET-010/v001/cleanup.py
Requires Pillow, NumPy, SciPy. No extracted game art is used.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'raw/slash.png'
source = np.asarray(Image.open(SOURCE).convert('RGBA'))
GRAYS = np.array([32, 88, 144, 200, 255], dtype=np.int16)
CELL = (76, 142)
GAP = 8
# Generator emitted unequal whitespace: isolate each frame before equal packing.
CROPS = [(60, 550), (600, 1100), (1170, 1610)]
KEEP_COMPONENTS = [6, 7, 9]
SCALE = 108 / 790
sheet = Image.new('RGBA', (244, 142))
records = []
for index, ((x0, x1), keep) in enumerate(zip(CROPS, KEEP_COMPONENTS)):
    art = source[:, x0:x1].copy()
    mask = art[:, :, 3] >= 192
    labels, count = label(mask)
    sizes = np.bincount(labels.ravel())
    selected = np.argsort(sizes[1:])[::-1][:keep] + 1
    mask = np.isin(labels, selected)
    art[~mask] = 0
    art[mask, 3] = 255
    ys, xs = np.where(mask)
    bbox = (int(xs.min()), 94, int(xs.max()) + 1, 884)
    crop = Image.fromarray(art).crop(bbox)
    target = (round(crop.width * SCALE), 108)
    frame = np.asarray(crop.resize(target, Image.Resampling.NEAREST)).copy()
    valid = frame[:, :, 3] == 255
    gray = np.rint(frame[:, :, :3].astype(float).mean(axis=2))
    nearest = np.abs(gray[:, :, None] - GRAYS).argmin(axis=2)
    for channel in range(3):
        frame[:, :, channel] = np.where(valid, GRAYS[nearest], 0)
    frame[:, :, 3] = np.where(valid, 255, 0)
    offset = (index * 84 + (76 - target[0]) // 2, 17)
    sheet.paste(Image.fromarray(frame), offset)
    records.append({'frame': index, 'source_x_range': [x0, x1],
                    'retained_components': keep, 'native_art_size': list(target),
                    'native_offset': list(offset)})
sheet.save(ROOT / 'slash.png')
sheet.resize((976, 568), Image.Resampling.NEAREST).save(ROOT / 'slash_review_4x.png')
sheet.resize((122, 71), Image.Resampling.NEAREST).save(ROOT / 'slash_review_half.png')
data = np.asarray(sheet)
opaque = data[:, :, 3] == 255
colors = sorted({tuple(p) for p in data[opaque, :3].tolist()})
assert colors == [(int(g), int(g), int(g)) for g in GRAYS]
assert set(np.unique(data[:, :, 3])) == {0, 255}
assert not data[:, 76:84, 3].any() and not data[:, 160:168, 3].any()
assert not data[0, :, 3].any() and not data[-1, :, 3].any()
assert not data[:, 0, 3].any() and not data[:, -1, 3].any()
config = {'cell': list(CELL), 'frames': 3, 'gap': GAP,
          'timing_game_frames': [6, 4, 3], 'total_game_frames': 13,
          'loop': False, 'suggested_anchor': [38, 71],
          'runtime_anchor_verified': False, 'frames_processing': records,
          'cleanup': 'alpha >=192; retain largest components; shared isotropic scale; nearest-neighbor; exact gray snapping',
          'raw_dimensions': list(Image.open(SOURCE).size)}
(ROOT / 'processing.json').write_text(json.dumps(config, indent=2) + '\n')
checks = {'sheet_dimensions': list(sheet.size), 'opaque_palette': colors,
          'alpha_values': [0, 255], 'transparent_gap_width': GAP,
          'frame_count': 3, 'checks_passed': ['PNG complete decode', 'native sheet geometry',
          'five exact grays', 'binary alpha', 'empty frame gutters', 'no canvas edge clipping'],
          'sha256': hashlib.sha256((ROOT / 'slash.png').read_bytes()).hexdigest(),
          'unchecked': ['60fps in-game playback', 'runtime anchor placement', 'type tint playback'],
          'provenance': 'image_gen original generated abstract slash; approved original HIT reference'}
(ROOT / 'validation.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks))
