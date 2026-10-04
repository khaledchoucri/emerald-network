#!/usr/bin/env python3
"""Generate include/pkbn/bn6_gfx_data.h (battle effect pixels) from a bn6f checkout.

Usage: gen_bn6_gfx.py <bn6f dir> <out.h> [--preview out.png]

BN6 sprite archive layout (read from data/sprites/battleSpriteMegaMan.spr and checked by rendering):
  byte 3 = animation count; u32 offsets at +4 (relative to +4) -> animations;
  animation = 20-byte frames {u32 tileset, u32 palette, u32 subanim, u32 oam, u8 delay, u8 _, u8 flags, u8 _},
  flags 0x80 = last frame, 0x40 = loop; tileset/palette = u32 size then data;
  OAM list = 5-byte entries {tile, s8 x, s8 y, size, shape|0x40 hflip|0x80 vflip}, ends with 0xFF.
Compressed entries (COMPRESSED_PTR_FLAG in data/SpritePointersList.s) are GBA LZ77 with a 4-byte size prefix.
"""
import os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx_curated import FX

SHAPES = {(0,0):(8,8),(0,1):(16,16),(0,2):(32,32),(0,3):(64,64),(1,0):(16,8),(1,1):(32,8),(1,2):(32,16),(1,3):(64,32),
          (2,0):(8,16),(2,1):(8,32),(2,2):(16,32),(2,3):(32,64)}

def lz77(b):
    assert b[0] == 0x10
    n = struct.unpack_from('<I', b, 0)[0] >> 8; out = bytearray(); o = 4
    while len(out) < n:
        fl = b[o]; o += 1
        for i in range(8):
            if len(out) >= n: break
            if fl & (0x80 >> i):
                b1, b2 = b[o], b[o+1]; o += 2
                ln = (b1 >> 4) + 3; d = ((b1 & 15) << 8 | b2) + 1
                for _ in range(ln): out.append(out[-d])
            else:
                out.append(b[o]); o += 1
    return bytes(out)

def load_lists(root):
    labels = {}
    for f in ['data.s'] + ['data/' + x for x in os.listdir(os.path.join(root, 'data')) if x.endswith('.s')]:
        txt = open(os.path.join(root, f), errors='replace').read().split('\n')
        for i, l in enumerate(txt):
            m = re.match(r'^(\w+)::', l)
            if m and i + 1 < len(txt):
                m2 = re.search(r'\.incbin "([^"]+)"', txt[i+1])
                if m2:
                    labels[m.group(1)] = m2.group(1)
                elif re.match(r'\s*\.(byte|hword|word)\s', txt[i+1]):
                    labels[m.group(1)] = (f, i + 1)  # inline data in a .s file
    cats = []
    for l in open(os.path.join(root, 'data/SpritePointersList.s')).read().split('\n'):
        m = re.match(r'^(\w+)::', l)
        if m: cats.append([])
        m = re.match(r'\s*\.word (\w+)( \+ COMPRESSED_PTR_FLAG)?', l)
        if m and cats: cats[-1].append((m.group(1), bool(m.group(2))))
    return labels, cats[1:]  # first block is the list of lists itself

def sprite_bytes(root, labels, cats, cat, idx):
    name, comp = cats[cat][idx]
    src = labels[name]
    if isinstance(src, tuple):
        data = inline_bytes(root, *src)
    else:
        data = open(os.path.join(root, src), 'rb').read()
    return lz77(data)[4:] if comp else data

def inline_bytes(root, f, start):
    out = bytearray()
    for l in open(os.path.join(root, f), errors='replace').read().split('\n')[start:]:
        l = l.split('//')[0].strip()
        if not l or re.match(r'^\w+::?$', l): continue  # labels inside a sprite's data
        m = re.match(r'\.(byte|hword|word)\s+(.*)', l)
        if not m: break
        size = {'byte': 1, 'hword': 2, 'word': 4}[m.group(1)]
        for v in m.group(2).split(','):
            out += (int(v.strip(), 0) & ((1 << (8 * size)) - 1)).to_bytes(size, 'little')
    return bytes(out)

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def frames(b, anim):
    base = 4
    o = base + u32(b, 4 + 4 * anim); out = []
    while True:
        ts, pal, sub, oam = struct.unpack_from('<4I', b, o); delay = b[o+16]; fl = b[o+18]
        out.append((ts, pal, oam, delay, fl)); o += 20
        if fl & 0xC0 or len(out) > 64: break
    return out, bool(out[-1][4] & 0x40)

def render(b, fr):
    ts, pal, oam, delay, fl = fr
    base = 4
    tso = base + ts; tiles = b[tso+4:tso+4+u32(b, tso)]
    po = base + pal + 4
    palette = [struct.unpack_from('<H', b, po + 2*i)[0] & 0x7FFF for i in range(16)]
    oo = base + oam; lo = oo + u32(b, oo)
    px = {}
    while True:
        t, x, y, sz, f = struct.unpack_from('<BbbBB', b, lo); lo += 5
        if t == 0xFF and sz == 0xFF: break
        w, h = SHAPES[(f & 3, sz & 3)]; tw = w // 8
        for ty in range(h // 8):
            for tx in range(tw):
                ti = t + ty * tw + tx
                for py in range(8):
                    for pxx in range(8):
                        k = ti * 32 + py * 4 + pxx // 2
                        if k >= len(tiles): continue
                        c = (tiles[k] >> 4) if pxx & 1 else tiles[k] & 15
                        if not c: continue
                        X = tx * 8 + pxx; Y = ty * 8 + py
                        if f & 0x40: X = w - 1 - X
                        if f & 0x80: Y = h - 1 - Y
                        px[(x + X, y + Y)] = c
    if not px:
        return dict(w=1, h=1, ox=0, oy=0, px=[0], pal=palette, delay=delay)
    xs = [p[0] for p in px]; ys = [p[1] for p in px]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    arr = [0] * (w * h)
    for (X, Y), c in px.items(): arr[(Y - y0) * w + (X - x0)] = c
    return dict(w=w, h=h, ox=x0, oy=y0, px=arr, pal=palette, delay=delay)

def main():
    root, out = sys.argv[1], sys.argv[2]
    preview = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    labels, cats = load_lists(root)
    allf = []; anims = []
    for name, cat, idx, anim in FX:
        b = sprite_bytes(root, labels, cats, cat, idx)
        frs, loop = frames(b, anim)
        first = len(allf)
        for fr in frs: allf.append(render(b, fr))
        anims.append((name, first, len(frs), loop))
    L = ['// GENERATED by tools/gen_bn6_gfx.py from upstream/bn6f (data/sprites, data/compressed).',
         '// Contains extracted BN6 graphics: never commit this file.', '']
    pals = {}
    for i, f in enumerate(allf):
        key = tuple(f['pal'])
        if key not in pals:
            pals[key] = len(pals)
            L.append('static const u16 sBn6Pal%d[16] = {%s};' % (pals[key], ','.join('0x%04X' % c for c in key)))
        L.append('static const u8 sBn6Px%d[%d] = {%s};' % (i, len(f['px']), ','.join(str(c) for c in f['px'])))
    L.append('')
    L.append('static const struct PkbnFxFrame sBn6Frames[%d] = {' % len(allf))
    for i, f in enumerate(allf):
        L.append('    {{%d, %d, %d, %d, sBn6Px%d, sBn6Pal%d}, %d},' % (f['w'], f['h'], f['ox'], f['oy'], i, pals[tuple(f['pal'])], max(1, f['delay'])))
    L.append('};')
    L.append('static const struct PkbnFxAnim sBn6Anims[FX_COUNT] = {')
    for name, first, n, loop in anims:
        L.append('    [FX_%s] = {%d, %d, %d},' % (name, first, n, int(loop)))
    L.append('};')
    open(out, 'w').write('\n'.join(L) + '\n')
    print('bn6 fx: %d effects, %d frames, %d palettes -> %s' % (len(anims), len(allf), len(pals), out))
    if preview:
        from PIL import Image, ImageDraw
        cell = 72; cols = max(n for _, _, n, _ in anims)
        sh = Image.new('RGB', (110 + cell * cols, cell * len(anims)), (24, 24, 40)); d = ImageDraw.Draw(sh)
        for r, (name, first, n, loop) in enumerate(anims):
            d.text((2, r * cell + 2), name + (' (loop)' if loop else ''), fill=(255, 255, 0))
            for k in range(n):
                f = allf[first + k]
                for i, c in enumerate(f['px']):
                    if c:
                        col = f['pal'][c]
                        X = 110 + k * cell + cell // 2 + f['ox'] + i % f['w']; Y = r * cell + cell // 2 + 10 + f['oy'] + i // f['w']
                        if 0 <= X < sh.width and r * cell <= Y < (r + 1) * cell:
                            sh.putpixel((X, Y), ((col & 31) << 3, ((col >> 5) & 31) << 3, ((col >> 10) & 31) << 3))
        sh.save(preview)

if __name__ == '__main__':
    main()
