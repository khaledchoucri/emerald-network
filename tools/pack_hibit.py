#!/usr/bin/env python3
"""POC-24 (POC-28: all of ASSET-003..010): packs our own hi-bit battle art (Codex's approved source sheets under poc/assets/generated/) into a C header
for the host build: include/pkbn/hibit_gfx_data.h. Run by scripts/setup_host.sh; the header is generated, not committed.

    python3 tools/pack_hibit.py <project dir> <out header>

What it does to the sources (see docs/asset-workflow/requests/ASSET-003 and ASSET-004, "Integration"):
- Panels (ASSET-003 v002): each sheet row is six equal cells; every cell is shrunk to 88x52 by area average, reduced to
  16 colours, and its alpha made hard (the BROKEN hole stays transparent). The front edge is shrunk to 88 wide and
  trimmed (not squashed) to 12 rows by dropping rows from its middle.
- Fire (ASSET-004 v001 FIREBALL, v002 the other four): alpha made hard, specks dropped, frames split at the gaps,
  one scale per effect (so growing frames keep their sizes), shrunk by area average, up to 31 colours per effect.
  Each effect is fitted into the area BN6's own frames cover around their anchor (measured from sBn6Frames, doubled),
  so it lands where today's effect does. FIREBALL and FLAME_JET are mirrored to face left like BN6's (the game flips
  them by direction).
- POC-28, impacts (ASSET-006) and strikes (ASSET-010): drawn at hi-bit size on cells that are BN6's extents x2, so each
  frame is placed centred on BN6's box at 1:1. Grey ones keep the five greys as indices 1..5 (the game swaps in the
  type's ramp, packed from type_ramps.json); explosions and smoke keep their colours.
- POC-28, still pictures: the backdrop with its motes and streams (ASSET-005), the HUD (ASSET-007), the Custom screen
  (ASSET-009) and the Program Advance parts (ASSET-008), each up to 64 colours, grey parts as indices 1..5 for the game
  to colour (include/pkbn/gfx.h HI_*).
"""
import os
import sys

import numpy as np
from PIL import Image

PANEL_W, PANEL_H, LIP_H = 88, 52, 12
# sheet order (ASSET-003): NORMAL CRACKED BROKEN POISON HOLY GRASS / ICE LAVA UP DOWN LEFT RIGHT
# game order (include/pkbn/grid_internal.h): NORMAL CRACKED BROKEN POISON HOLY GRASS ICE UP DOWN LEFT RIGHT LAVA
SHEET_TO_GAME = [0, 1, 2, 3, 4, 5, 6, 11, 7, 8, 9, 10]

# BN6 frames' extent around the anchor at 1x (x0, x1, y0, y1), from sBn6Frames (tools/gen_bn6_gfx.py output), and
# how our art sits in it: (horizontal: 'left' | 'right' | 'centre', vertical: 'bottom' | 'centre', mirror)
FIRE = [
    # name, file, frames, delay, loops, BN6 extent, align, mirror
    ('FIREBALL', 'ASSET-004/v001/fireball_source.png', 3, 2, 1, (2, 47, -18, 14), ('left', 'centre'), True),
    ('FIRE_BURST', 'ASSET-004/v002/fire_burst_source.png', 4, 6, 0, (-17, 17, -45, 8), ('centre', 'bottom'), False),
    ('FLAME_JET', 'ASSET-004/v002/flame_jet_source.png', 3, 2, 1, (-93, 8, -49, 12), ('right', 'centre'), True),
    ('FIRE_TALL', 'ASSET-004/v002/fire_tall_source.png', 3, 2, 1, (-20, 19, -52, 5), ('centre', 'bottom'), False),
    ('FIRE_PANEL', 'ASSET-004/v002/fire_panel_source.png', 3, 2, 1, (-16, 16, -46, 8), ('centre', 'bottom'), False),
]


def bgr555(r, g, b):
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10) | 0x8000


def shrink(img, size):
    """area-average shrink of an RGBA image with premultiplied alpha (no dark fringes), then hard alpha"""
    out = img.convert('RGBa').resize(size, Image.BOX).convert('RGBA')
    a = np.array(out)
    a[:, :, 3] = np.where(a[:, :, 3] >= 128, 255, 0)
    return Image.fromarray(a)


def quantize(imgs, colours):
    """-> (palette [(r,g,b)], [index arrays]) shared by imgs; index 0 = transparent"""
    w = sum(i.width for i in imgs); h = max(i.height for i in imgs)
    strip = Image.new('RGB', (w, h)); x = 0
    for i in imgs:
        strip.paste(i.convert('RGB'), (x, 0)); x += i.width
    q = strip.quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    colours = min(colours, len(q.getpalette()) // 3)   # (POC-28) art with fewer colours than asked for
    pal = q.getpalette()[:colours * 3]
    idx = np.array(q); outs = []; x = 0
    for i in imgs:
        a = np.array(i)[:, :, 3]
        part = idx[:i.height, x:x + i.width].astype(np.int32) + 1
        part[a == 0] = 0
        outs.append(part.astype(np.uint8)); x += i.width
    return [tuple(pal[k * 3:k * 3 + 3]) for k in range(colours)], outs


def hard_alpha(img, min_area=24):
    """alpha >= 128 -> opaque, the rest clear; drops specks smaller than min_area pixels (source scale)"""
    a = np.array(img.convert('RGBA'))
    solid = a[:, :, 3] >= 128
    try:
        from scipy import ndimage
        lab, n = ndimage.label(solid)
        sizes = ndimage.sum(solid, lab, range(1, n + 1))
        for k, sz in enumerate(sizes, 1):
            if sz < min_area:
                solid[lab == k] = False
    except ImportError:
        pass
    a[:, :, 3] = np.where(solid, 255, 0)
    a[~solid] = 0
    return Image.fromarray(a)


def split_frames(img, n):
    """frames left to right, cut at the n-1 widest empty column gaps, each cropped to its content"""
    al = np.array(img)[:, :, 3] > 0
    cols = np.where(al.any(0))[0]
    gaps = [(cols[i + 1] - cols[i], cols[i], cols[i + 1]) for i in range(len(cols) - 1) if cols[i + 1] - cols[i] > 1]
    cuts = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    bounds = [cols[0]] + [(g[1] + g[2]) // 2 for g in cuts] + [cols[-1] + 1]
    frames = []
    for i in range(n):
        f = img.crop((bounds[i], 0, bounds[i + 1], img.height))
        frames.append(f.crop(f.getbbox()))
    return frames


def panels(src_dir):
    out = {}
    for side, name in ((0, 'red'), (1, 'blue')):
        im = Image.open(os.path.join(src_dir, 'ASSET-003/v002/panels_%s_source.png' % name)).convert('RGBA')
        al = np.array(im)[:, :, 3] >= 128
        rows = np.where(al.any(1))[0]
        bands = []                                            # vertical runs of art: two panel rows, then the lip
        start = rows[0]
        for i in range(1, len(rows)):
            if rows[i] != rows[i - 1] + 1:
                bands.append((start, rows[i - 1] + 1)); start = rows[i]
        bands.append((start, rows[-1] + 1))
        if len(bands) == 2:                                   # the two panel rows touch (blue v002): halve the band
            (a0, a1), lipband = bands
            bands = [(a0, (a0 + a1) // 2), ((a0 + a1) // 2, a1), lipband]
        assert len(bands) == 3, '%s: expected 2 panel rows and the front edge, found %d bands' % (name, len(bands))
        cells = []
        for (y0, y1) in bands[:2]:
            cols = np.where(al[y0:y1].any(0))[0]
            x0, x1 = cols[0], cols[-1] + 1
            w = (x1 - x0) / 6
            for i in range(6):
                cells.append(im.crop((round(x0 + i * w), y0, round(x0 + (i + 1) * w), y1)))
        imgs = [None] * 12
        for k, c in enumerate(cells):
            imgs[SHEET_TO_GAME[k]] = shrink(c, (PANEL_W, PANEL_H))
        # the front edge: shrink to 88 wide, then drop rows from the middle down to 12
        y0, y1 = bands[2]
        cols = np.where(al[y0:y1].any(0))[0]
        lip = im.crop((cols[0], y0, cols[-1] + 1, y1))
        h = max(LIP_H, round(lip.height * PANEL_W / lip.width))
        lip = shrink(lip, (PANEL_W, h))
        if h > LIP_H:
            a = np.array(lip); keep = list(range(LIP_H // 2)) + list(range(h - (LIP_H - LIP_H // 2), h))
            lip = Image.fromarray(a[keep])
        out[side] = (imgs, lip)
    return out


def fire(src_dir):
    effects = []
    for name, rel, n, delay, loops, (bx0, bx1, by0, by1), (ah, av), mirror in FIRE:
        im = hard_alpha(Image.open(os.path.join(src_dir, rel)))
        frames = split_frames(im, n)
        if mirror:
            frames = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]
        tx0, tx1, ty0, ty1 = bx0 * 2, bx1 * 2, by0 * 2, by1 * 2          # the target area at 2x
        mw = max(f.width for f in frames); mh = max(f.height for f in frames)
        s = min((tx1 - tx0) / mw, (ty1 - ty0) / mh)
        placed = []
        for f in frames:
            g = shrink(f, (max(1, round(f.width * s)), max(1, round(f.height * s))))
            bb = g.getbbox() or (0, 0, g.width, g.height)
            g = g.crop(bb)
            ox = tx0 if ah == 'left' else tx1 - g.width if ah == 'right' else (tx0 + tx1) // 2 - g.width // 2
            oy = ty1 - g.height if av == 'bottom' else (ty0 + ty1) // 2 - g.height // 2
            placed.append((g, ox, oy))
        pal, idx = quantize([p[0] for p in placed], 31)
        effects.append((name, delay, loops, pal, [(p[0].width, p[0].height, p[1], p[2], i) for p, i in zip(placed, idx)]))
    return effects


# ---- POC-28: ASSET-005..010 (all approved) ------------------------------------------------------------------------
GREYS = [(0x20, 0x20, 0x20), (0x58, 0x58, 0x58), (0x90, 0x90, 0x90), (0xc8, 0xc8, 0xc8), (0xff, 0xff, 0xff)]
TYPE_ORDER = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', None, 'Fire',
              'Water', 'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark']   # the game's TYPE_* ids (9 = ???)

# effect sheets drawn at hi-bit size already (their cells are BN6's extents x2): fx id, file, cell w, frames, holds,
# grey (tinted by the type ramp) or colour, BN6 extent at 1x (x0, x1, y0, y1) the cell is centred on
EFFECTS = [
    ('HIT', 'ASSET-006/v001/hit.png', 64, 6, [1, 1, 2, 2, 2, 2], True, (-16, 16, -16, 16)),
    ('HIT_SMALL', 'ASSET-006/v002/hit_small.png', 64, 4, [1, 1, 1, 1], True, (-15, 16, -12, 16)),
    ('HIT_STAR', 'ASSET-006/v002/hit_star.png', 92, 5, [2, 3, 3, 2, 2], True, (-27, 19, -37, 6)),
    ('DUST', 'ASSET-006/v002/dust.png', 64, 4, [2, 2, 2, 2], True, (-21, 11, -12, 11)),
    ('EXPLODE', 'ASSET-006/v002/explode.png', 112, 6, [2, 4, 4, 4, 4, 4], False, (-24, 32, -24, 32)),
    ('EXPLODE_SMALL', 'ASSET-006/v002/explode_small.png', 64, 6, [2, 3, 3, 3, 4, 4], False, (-16, 16, -31, 16)),
    ('SMOKE', 'ASSET-006/v002/smoke.png', 48, 8, [2] * 8, False, (-7, 8, -8, 8)),
    ('SLASH', 'ASSET-010/v002/slash.png', 76, 4, [4, 4, 3, 3], True, (-22, 15, -35, 36)),
    ('SLASH_ARC', 'ASSET-010/v002/slash_arc.png', 142, 5, [1, 3, 3, 3, 1], True, (-41, 30, -52, 36)),
    ('CLAW', 'ASSET-010/v002/claw.png', 84, 5, [1, 3, 3, 3, 1], True, (-28, 14, -56, 46)),
    ('HI_STAB', 'ASSET-010/v002/stab.png', 62, 2, [3, 2], True, (-15, 16, -6, 7)),
    ('HI_JAWS', 'ASSET-010/v002/jaws.png', 64, 5, [3, 3, 2, 6, 6], True, (-16, 16, -24, 24)),
]


def grey_index(img):
    """RGBA in the five greys -> indices 1..5 (darkest first), 0 = clear"""
    a = np.array(img.convert('RGBA'))
    idx = np.zeros(a.shape[:2], np.uint8)
    for k, g in enumerate(GREYS, 1):
        idx[(a[:, :, 3] > 0) & (np.abs(a[:, :, :3].astype(int) - g).sum(2) <= 24)] = k
    left = (a[:, :, 3] > 0) & (idx == 0)
    if left.any():   # off-grey pixels (none in the approved sheets): nearest grey by brightness
        lum = a[:, :, :3].mean(2)
        idx[left] = 1 + np.abs(lum[left, None] - np.array([g[0] for g in GREYS])[None]).argmin(1)
    return idx


def effects(src_dir):
    out = []
    for name, rel, cw, n, holds, grey, (bx0, bx1, by0, by1) in EFFECTS:
        im = Image.open(os.path.join(src_dir, rel)).convert('RGBA')
        ch = im.height
        cx, cy = bx0 + bx1, by0 + by1                       # the BN6 box's centre at 2x
        frames = []
        for i in range(n):
            cell = im.crop((i * (cw + 8), 0, i * (cw + 8) + cw, ch))
            bb = cell.getbbox() or (0, 0, 1, 1)
            frames.append((cell.crop(bb), cx - cw // 2 + bb[0], cy - ch // 2 + bb[1]))
        if grey:
            pal = GREYS
            idx = [grey_index(f[0]) for f in frames]
        else:
            pal, idx = quantize([f[0] for f in frames], 31)
        out.append((name, holds, grey, pal, [(f[0].width, f[0].height, f[1], f[2], i) for f, i in zip(frames, idx)]))
    return out


def ramps(src_dir):
    import json
    j = json.load(open(os.path.join(src_dir, 'ASSET-006/v002/type_ramps.json')))
    rows = []
    for t in TYPE_ORDER:
        hexes = j['ramps'][t] if t else ['#202020', '#585858', '#909090', '#c8c8c8', '#ffffff']
        rows.append([tuple(int(h[k:k + 2], 16) for k in (1, 3, 5)) for h in hexes])
    return rows


# still pictures (name, file, crop box or None, grey: True = the five greys as indices 1..5 for the game to tint)
STILLS = [
    ('BACKDROP', 'ASSET-005/v002/backdrop.png', None, False),
    ('H1_PLAYER', 'ASSET-007/v002/player.png', None, False),
    ('H1_FOE', 'ASSET-007/v002/foe.png', None, False),
    ('H1_SYNC1', 'ASSET-007/v002/synchro1.png', None, False),
    ('H1_SYNC2', 'ASSET-007/v002/synchro2.png', None, False),
    ('H2_TAG', 'ASSET-007/v003/h2_tag.png', None, True),
    ('H3_TROUGH', 'ASSET-007/v003/h3_trough.png', None, False),
    ('H3_FILL', 'ASSET-007/v003/h3_fill.png', None, True),
    ('H4_FRAME', 'ASSET-007/v003/h4_frame.png', None, False),
    ('H4_FILL', 'ASSET-007/v003/h4_fill.png', None, True),
    ('H4_FULL1', 'ASSET-007/v003/h4_full_1.png', None, False),
    ('H4_FULL2', 'ASSET-007/v003/h4_full_2.png', None, False),
    ('H4_FULL3', 'ASSET-007/v003/h4_full_3.png', None, False),
    ('H4_FULL4', 'ASSET-007/v003/h4_full_4.png', None, False),
    ('H5_LINE', 'ASSET-007/v003/h5_line.png', None, False),
    ('C1_WINDOW', 'ASSET-009/v002/window_body.png', None, False),
    ('C2_ART', 'ASSET-009/v002/art_frame.png', None, False),
    ('C3_SLOT', 'ASSET-009/v002/slot.png', None, True),
    ('C5_OK1', 'ASSET-009/v002/ok.png', (0, 0, 44, 56), False),
    ('C5_OK2', 'ASSET-009/v002/ok.png', (52, 0, 96, 56), False),
    ('C4_TL1', 'ASSET-009/v002/cursor.png', (0, 0, 12, 12), False),
    ('C4_TR1', 'ASSET-009/v002/cursor.png', (20, 0, 32, 12), False),
    ('C4_BL1', 'ASSET-009/v002/cursor.png', (40, 0, 52, 12), False),
    ('C4_BR1', 'ASSET-009/v002/cursor.png', (60, 0, 72, 12), False),
    ('C4_TL2', 'ASSET-009/v002/cursor.png', (80, 0, 92, 12), False),
    ('C4_TR2', 'ASSET-009/v002/cursor.png', (100, 0, 112, 12), False),
    ('C4_BL2', 'ASSET-009/v002/cursor.png', (120, 0, 132, 12), False),
    ('C4_BR2', 'ASSET-009/v002/cursor.png', (140, 0, 152, 12), False),
    ('C6_TAB', 'ASSET-009/v002/chosen_tab.png', None, True),
    ('C7_PA1', 'ASSET-009/v002/pa_preview.png', (0, 0, 168, 52), False),
    ('C7_PA2', 'ASSET-009/v002/pa_preview.png', (176, 0, 344, 52), False),
] + [('MOTE_%d_%d' % (r, f), 'ASSET-005/v003/motes.png', (f * 14, r * 14, f * 14 + 6, r * 14 + 6), False)
     for r in range(3) for f in range(4)] \
  + [('STREAM_%d' % k, 'ASSET-005/v003/data_streams.png', (k * 16, 0, k * 16 + 8, 120), False) for k in range(4)] \
  + [('PA_CARD_%d' % k, 'ASSET-008/v002/card_flip.png', (k * 80, 0, k * 80 + 72, 88), False) for k in range(4)] \
  + [('PA_TRAIL_%d' % k, 'ASSET-008/v002/trail.png', (k * 104, 0, k * 104 + 96, 24), True) for k in range(4)] \
  + [('PA_EMBLEM_%d' % k, 'ASSET-008/v002/emblem.png', (k * 136, 0, k * 136 + 128, 128), False) for k in range(7)] \
  + [('PA_BURST_%d' % k, 'ASSET-008/v002/burst.png', (k * 216, 0, k * 216 + 208, 208), True) for k in range(6)] \
  + [('PA_BANNER', 'ASSET-008/v002/banner.png', None, False)] \
  + [('PA_SHINE_%d' % k, 'ASSET-008/v002/shine.png', (k * 248, 0, k * 248 + 240, 36), False) for k in range(4)] \
  + [('PA_SYM_%d' % k, 'ASSET-008/v003/type_symbols.png', (k * 40, 0, k * 40 + 32, 32), True) for k in range(17)]


def stills(src_dir):
    out = []
    for name, rel, box, grey in STILLS:
        im = Image.open(os.path.join(src_dir, rel)).convert('RGBA')
        if box:
            im = im.crop(box)
        a = np.array(im); a[:, :, 3] = np.where(a[:, :, 3] >= 128, 255, 0); im = Image.fromarray(a)
        if grey:
            out.append((name, im.width, im.height, GREYS, grey_index(im)))
        else:
            pal, (idx,) = quantize([im], min(64, max(2, len({tuple(p) for p in a[a[:, :, 3] > 0][:, :3]}))))
            out.append((name, im.width, im.height, pal, idx))
    return out


def c_bytes(arr):
    flat = [str(int(v)) for v in arr.flatten()]
    return ',\n    '.join(','.join(flat[i:i + 32]) for i in range(0, len(flat), 32))


def main():
    project, out_path = sys.argv[1], sys.argv[2]
    src = os.path.join(project, 'poc', 'assets', 'generated')
    lines = ['// GENERATED by tools/pack_hibit.py from poc/assets/generated (our own art: ASSET-003..010).',
             '// Hi-bit (2x) images: w, h, ox, oy in buffer pixels. Not committed: scripts/setup_host.sh rebuilds it.',
             '#define PKBN_HIBIT_PANEL_TYPES 12', '#define PKBN_HIBIT_VERSION 2', '']
    P = panels(src)
    for side in (0, 1):
        imgs, lip = P[side]
        for t, img in enumerate(imgs + [lip]):
            pal, (idx,) = quantize([img], 16)
            nm = 'Panel%d_%d' % (side, t)
            lines.append('static const u16 sHiPal_%s[17] = {0x0000,%s};' % (nm, ','.join('0x%04X' % bgr555(*c) for c in pal)))
            lines.append('static const u8 sHiPx_%s[%d] = {\n    %s};' % (nm, idx.size, c_bytes(idx)))
    lines.append('static const struct PkbnImage sHiPanel[2][PKBN_HIBIT_PANEL_TYPES] = {')
    for side in (0, 1):
        lines.append('    {' + ', '.join('{%d, %d, 0, 0, sHiPx_Panel%d_%d, sHiPal_Panel%d_%d, 1}' % (PANEL_W, PANEL_H, side, t, side, t)
                                         for t in range(12)) + '},')
    lines.append('};')
    lines.append('static const struct PkbnImage sHiLip[2] = {' + ', '.join(
        '{%d, %d, 0, 0, sHiPx_Panel%d_12, sHiPal_Panel%d_12, 1}' % (PANEL_W, LIP_H, s, s) for s in (0, 1)) + '};')
    lines.append('')
    frames_c, table_c, first = [], [], 0
    for name, delay, loops, pal, frames in fire(src):
        lines.append('static const u16 sHiPal_%s[%d] = {0x0000,%s};' % (name, len(pal) + 1, ','.join('0x%04X' % bgr555(*c) for c in pal)))
        for k, (w, h, ox, oy, idx) in enumerate(frames):
            lines.append('static const u8 sHiPx_%s_%d[%d] = {\n    %s};' % (name, k, idx.size, c_bytes(idx)))
            frames_c.append('    {{%d, %d, %d, %d, sHiPx_%s_%d, sHiPal_%s, 1}, %d},' % (w, h, ox, oy, name, k, name, delay))
        table_c.append('    {FX_%s, %d, %d, %d, 0},' % (name, first, len(frames), loops))
        first += len(frames)
    # POC-28: impacts (ASSET-006) and strikes (ASSET-010); grey ones are tinted at draw time by the type ramp
    for name, holds, grey, pal, frames in effects(src):
        lines.append('static const u16 sHiPal_%s[%d] = {0x0000,%s};' % (name, len(pal) + 1, ','.join('0x%04X' % bgr555(*c) for c in pal)))
        for k, (w, h, ox, oy, idx) in enumerate(frames):
            lines.append('static const u8 sHiPx_%s_%d[%d] = {\n    %s};' % (name, k, idx.size, c_bytes(idx)))
            frames_c.append('    {{%d, %d, %d, %d, sHiPx_%s_%d, sHiPal_%s, 1}, %d},' % (w, h, ox, oy, name, k, name, holds[k]))
        table_c.append('    {FX_%s, %d, %d, %d, %d},' % (name, first, len(frames), 0, 1 if grey else 0))
        first += len(frames)
    lines.append('static const struct PkbnFxFrame sHiFxFrames[%d] = {' % first)
    lines += frames_c + ['};']
    lines.append('static const struct { u8 fx; u8 first; u8 count; u8 loop; u8 grey; } sHiFx[%d] = {' % len(table_c))
    lines += table_c + ['};', '']
    # the type ramps (ASSET-006 part C): palette index 1..5 = outline, shade, base, light, highlight, by TYPE_* id
    lines.append('#define PKBN_HIBIT_RAMPS 1')
    lines.append('static const u16 sHiRamp[%d][6] = {' % len(TYPE_ORDER))
    for row in ramps(src):
        lines.append('    {0x0000,%s},' % ','.join('0x%04X' % bgr555(*c) for c in row))
    lines.append('};')
    # still pictures: the backdrop, the HUD (ASSET-007), the Custom screen (ASSET-009)
    lines.append('#define PKBN_HIBIT_STILLS 1')
    names = []
    for name, w, h, pal, idx in stills(src):
        lines.append('static const u16 sHiPal_%s[%d] = {0x0000,%s};' % (name, len(pal) + 1, ','.join('0x%04X' % bgr555(*c) for c in pal)))
        lines.append('static const u8 sHiPx_%s[%d] = {\n    %s};' % (name, idx.size, c_bytes(idx)))
        names.append('    [HI_%s] = {%d, %d, 0, 0, sHiPx_%s, sHiPal_%s, 1},' % (name, w, h, name, name))
    lines.append('static const struct PkbnImage sHiStill[HI_STILL_COUNT] = {')
    lines += names + ['};', '']
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    open(out_path, 'w').write('\n'.join(lines))
    print('pack_hibit: wrote %s (24 panels, 2 front edges, %d effect frames, %d stills)' % (out_path, first, len(STILLS)))


if __name__ == '__main__':
    main()
