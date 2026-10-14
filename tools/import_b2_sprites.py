#!/usr/bin/env python3
"""POC-25: imports the animated Pokémon battle sprites from the player's own Pokémon Black 2 / White 2 (.nds) into
pkbn_b2_sprites.bin, which the game loads at startup (src/pkbn/monsprite.c). The file holds Nintendo's sprites, so it is
never committed (CLAUDE.md rule 6): scripts/setup_host.sh builds it when PKBN_SPRITE_ROM points at the player's copy.

    python3 tools/import_b2_sprites.py <game.nds | a004.narc> <out.bin> [--xbrz /path/libxbrz.so] [--max-species 386]

What it does (docs: poc/POC-25.md):
- Gen 5 battle sprites live in the ROM's archive a/0/0/4: 20 files per species (front 0-8, back 9-17, palettes 18-19;
  magical/pokemon-nds-sprites docs/pokegra.rst). We take the front (the battle is side-on; the player's is mirrored).
- Each is a cut-out puppet: a parts sheet (NCGR, 2D mapping), cells of parts (NCER), cell animations that rotate /
  scale / move them (NANR), poses of cells (NMCR) and the pose sequence (NMAR). Formats as worked out in POC-25.
- The parts sheet is upscaled 2x with xBRZ (or Scale2x when xBRZ isn't available) and snapped back to the sprite's own
  16 colours, so it stays pixel art in its own palette; the shiny palette is kept too.
"""
import ctypes
import math
import os
import struct
import sys

import numpy as np

MAGIC = b'PKBNB2S1'


# ---- NDS file system and NARC ------------------------------------------------------------------------------------
def nds_file(rom, path):
    fnt_off, fnt_size, fat_off, fat_size = struct.unpack_from('<IIII', rom, 0x40)

    def dir_entries(dir_id):
        sub_off, first_id, _ = struct.unpack_from('<IHH', rom, fnt_off + (dir_id & 0xFFF) * 8)
        p = fnt_off + sub_off; fid = first_id
        while True:
            t = rom[p]; p += 1
            if t == 0:
                return
            name = rom[p:p + (t & 0x7F)].decode('latin-1'); p += t & 0x7F
            if t & 0x80:
                sub = struct.unpack_from('<H', rom, p)[0]; p += 2
                yield name, True, sub
            else:
                yield name, False, fid; fid += 1

    cur = 0xF000
    parts = path.split('/')
    for i, part in enumerate(parts):
        for name, is_dir, ident in dir_entries(cur):
            if name == part:
                if i == len(parts) - 1:
                    start, end = struct.unpack_from('<II', rom, fat_off + ident * 8)
                    return rom[start:end]
                cur = ident
                break
        else:
            raise KeyError(path)


def narc_files(data):
    assert data[:4] == b'NARC'
    o = struct.unpack_from('<H', data, 12)[0]          # header size
    assert data[o:o + 4] == b'BTAF'
    btaf_size, count = struct.unpack_from('<IH', data, o + 4)
    entries = [struct.unpack_from('<II', data, o + 12 + i * 8) for i in range(count)]
    o += btaf_size
    assert data[o:o + 4] == b'BTNF'
    o += struct.unpack_from('<I', data, o + 4)[0]
    assert data[o:o + 4] == b'GMIF'
    base = o + 8
    return [data[base + s:base + e] for s, e in entries]


# ---- Nitro formats -----------------------------------------------------------------------------------------------
def lz(d):
    if not d or d[0] not in (0x10, 0x11):
        return bytes(d)
    out = bytearray(); size = d[1] | d[2] << 8 | d[3] << 16; i = 4
    if size == 0:
        size = struct.unpack_from('<I', d, 4)[0]; i = 8
    while len(out) < size:
        flags = d[i]; i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                if d[0] == 0x10:
                    ln = (d[i] >> 4) + 3; disp = ((d[i] & 0xF) << 8 | d[i + 1]) + 1; i += 2
                else:
                    b1 = d[i]; ind = b1 >> 4
                    if ind == 0:
                        ln = (((b1 & 0xF) << 4) | (d[i + 1] >> 4)) + 0x11; disp = ((d[i + 1] & 0xF) << 8 | d[i + 2]) + 1; i += 3
                    elif ind == 1:
                        ln = (((b1 & 0xF) << 12) | (d[i + 1] << 4) | (d[i + 2] >> 4)) + 0x111
                        disp = ((d[i + 2] & 0xF) << 8 | d[i + 3]) + 1; i += 4
                    else:
                        ln = ind + 1; disp = ((b1 & 0xF) << 8 | d[i + 1]) + 1; i += 2
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                out.append(d[i]); i += 1
    return bytes(out)


def blocks(d):
    hsize, nb = struct.unpack_from('<HH', d, 12)
    out = {}; o = hsize
    for _ in range(nb):
        out[d[o:o + 4].decode()] = d[o + 8:o + struct.unpack_from('<I', d, o + 4)[0]]
        o += struct.unpack_from('<I', d, o + 4)[0]
    return out


def nclr(d):
    b = blocks(lz(d))['TTLP']
    _, _, size, off = struct.unpack_from('<IIII', b, 0)
    raw = b[off:off + size]
    return [raw[i] | raw[i + 1] << 8 for i in range(0, 32, 2)]          # 16 BGR555 colours


def ncgr(d):
    b = blocks(lz(d))['RAHC']
    h, w = struct.unpack_from('<hh', b, 0)
    depth = struct.unpack_from('<I', b, 4)[0]
    size, off = struct.unpack_from('<II', b, 16)
    data = np.frombuffer(b[off:off + size], np.uint8)
    assert depth == 3, '4bpp expected'
    px = np.empty(data.size * 2, np.uint8); px[0::2] = data & 15; px[1::2] = data >> 4
    return px.reshape(h * 8, w * 8), w                                  # a scanned (bitmap) sheet, 2D mapping


SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
         (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def ncer(d):
    b = blocks(lz(d))['KBEC']
    count, battr, off = struct.unpack_from('<HHI', b, 0)
    es = 16 if battr == 1 else 8
    cells = []
    for i in range(count):
        n, _, ooff = struct.unpack_from('<HHI', b, off + i * es)
        oams = []
        for k in range(n):
            a0, a1, a2 = struct.unpack_from('<HHH', b, off + count * es + ooff + k * 6)
            y = a0 & 0xFF; y = y - 256 if y >= 128 else y
            x = a1 & 0x1FF; x = x - 512 if x >= 256 else x
            w, h = SIZES[(a0 >> 14, a1 >> 14)]
            rs = bool(a0 & 0x100)
            if rs and a0 & 0x200:                     # double-size affine OBJ: the picture sits centred in 2w x 2h
                x += w // 2; y += h // 2
            oams.append((x, y, w, h, a2 & 0x3FF, (not rs) and bool(a1 & 0x1000), (not rs) and bool(a1 & 0x2000)))
        cells.append(oams)
    return cells


def nanr(d):
    """[(loop_start, [(duration, idx, rot, sx, sy, x, y)])]"""
    b = blocks(lz(d))['KNBA'] + bytes(32)
    na, _, aoff, foff, doff = struct.unpack_from('<HHIII', b, 0)
    anims = []
    for i in range(na):
        n, loop, etype, _, _, fo = struct.unpack_from('<HHHHII', b, aoff + i * 16)
        frames = []
        for k in range(n):
            eo, dur, _ = struct.unpack_from('<IHH', b, foff + fo + k * 8)
            p = doff + eo
            if etype == 0:
                e = (struct.unpack_from('<H', b, p)[0], 0, 4096, 4096, 0, 0)
            elif etype == 1:
                idx, rot, sx, sy, x, y = struct.unpack_from('<HHiihh', b, p); e = (idx, rot, sx, sy, x, y)
            else:
                idx, _, x, y = struct.unpack_from('<HHhh', b, p); e = (idx, 0, 4096, 4096, x, y)
            frames.append((dur,) + e)
        anims.append((min(loop, max(0, n - 1)), frames))
    return anims


def nmcr(d):
    b = blocks(lz(d))['KBCM']
    count, _, eoff, noff = struct.unpack_from('<HHII', b, 0)
    out = []
    for i in range(count):
        nn, _, no = struct.unpack_from('<HHI', b, eoff + i * 8)
        out.append([struct.unpack_from('<HhhH', b, noff + no + k * 8) for k in range(nn)])   # anim, x, y, flags
    return out


# ---- upscaling -----------------------------------------------------------------------------------------------------
def scale2x(a):
    p = np.pad(a, 1, mode='edge')
    E = p[1:-1, 1:-1]; B = p[:-2, 1:-1]; H = p[2:, 1:-1]; D = p[1:-1, :-2]; F = p[1:-1, 2:]
    out = np.empty((a.shape[0] * 2, a.shape[1] * 2), a.dtype)
    out[0::2, 0::2] = np.where((D == B) & (B != F) & (D != H), D, E)
    out[0::2, 1::2] = np.where((B == F) & (B != D) & (F != H), F, E)
    out[1::2, 0::2] = np.where((D == H) & (D != B) & (H != F), D, E)
    out[1::2, 1::2] = np.where((H == F) & (D != H) & (B != F), F, E)
    return out


class Upscaler:
    def __init__(self, lib):
        self.xb = None
        if lib and os.path.exists(lib):
            self.xb = ctypes.CDLL(lib)
            self.xb.xbrz_scale_defaults.argtypes = [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                                    ctypes.c_int, ctypes.c_int]

    def name(self):
        return 'xBRZ 2x, snapped to the palette' if self.xb else 'Scale2x (xBRZ not found)'

    def __call__(self, idx, pal):
        if self.xb is None:
            return scale2x(idx)
        P = np.array([((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31) for c in pal], np.int32)
        h, w = idx.shape
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., :3] = P[idx]; rgba[..., 3] = np.where(idx > 0, 255, 0)
        src = np.ascontiguousarray(rgba).view(np.uint32).reshape(h, w)
        dst = np.zeros((h * 2, w * 2), np.uint32)
        self.xb.xbrz_scale_defaults(2, src.ctypes.data, dst.ctypes.data, w, h, 2)    # ColorFormat::RGBA
        up = dst.view(np.uint8).reshape(h * 2, w * 2, 4).astype(np.int32)
        d = ((up[..., None, :3] - P[None, None, 1:, :]) ** 2).sum(-1)
        out = (d.argmin(-1) + 1).astype(np.uint8)
        out[up[..., 3] < 128] = 0
        return out


# ---- one species -----------------------------------------------------------------------------------------------------
def species_record(F, sp, up):
    b = sp * 20
    sheet, wt = ncgr(F[b + 2])
    pal, shiny = nclr(F[b + 18]), nclr(F[b + 19])
    big = up(sheet, pal)
    cells = ncer(F[b + 4]); anims = nanr(F[b + 5]); mcs = nmcr(F[b + 6]); seq = nanr(F[b + 7])
    out = bytearray()
    out += struct.pack('<16H16H', *(pal + shiny))
    # cells: each part's 2x pixels, 4bpp
    out += struct.pack('<H', len(cells))
    for oams in cells:
        out += struct.pack('<H', len(oams))
        for (x, y, w, h, tile, hf, vf) in oams:
            tx, ty = (tile % wt) * 8 * 2, (tile // wt) * 8 * 2
            blk = big[ty:ty + h * 2, tx:tx + w * 2]
            if blk.shape != (h * 2, w * 2):                              # (a part running off the sheet)
                pad = np.zeros((h * 2, w * 2), np.uint8); pad[:blk.shape[0], :blk.shape[1]] = blk; blk = pad
            if hf: blk = blk[:, ::-1]
            if vf: blk = blk[::-1, :]
            out += struct.pack('<hhHH', x * 2, y * 2, w * 2, h * 2)
            flat = blk.flatten()
            out += (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes()
    out += struct.pack('<H', len(anims))
    for loop, frames in anims:
        out += struct.pack('<HH', len(frames), loop)
        for (dur, idx, rot, sx, sy, x, y) in frames:
            out += struct.pack('<HHHhhhh', dur, idx, rot, max(-32768, min(32767, sx // 16)), max(-32768, min(32767, sy // 16)), x, y)
    out += struct.pack('<H', len(mcs))
    for nodes in mcs:
        out += struct.pack('<H', len(nodes))
        nodes = sorted(nodes, key=lambda n: -(n[3] >> 8))                 # back to front
        for (anim, x, y, fl) in nodes:
            out += struct.pack('<Hhh', anim, x, y)
    loop, frames = seq[0]
    out += struct.pack('<HH', len(frames), loop)
    for (dur, idx, rot, sx, sy, x, y) in frames:
        out += struct.pack('<HHhh', dur, idx, x, y)
    return bytes(out)


def main():
    args = sys.argv[1:]
    lib = None; max_sp = 386
    if '--xbrz' in args:
        i = args.index('--xbrz'); lib = args[i + 1]; del args[i:i + 2]
    if '--max-species' in args:
        i = args.index('--max-species'); max_sp = int(args[i + 1]); del args[i:i + 2]
    src, dst = args
    data = open(src, 'rb').read()
    if data[:4] != b'NARC':
        game = data[0x0C:0x10]
        assert game in (b'IRBO', b'IRAO', b'IREO', b'IRDO'), 'expects Pokemon Black 2 / White 2 / Black / White'
        data = nds_file(data, 'a/0/0/4')
    F = narc_files(data)
    up = Upscaler(lib)
    recs = [b''] + [species_record(F, sp, up) for sp in range(1, max_sp + 1)]
    out = bytearray(MAGIC) + struct.pack('<II', 1, len(recs))
    offs = []; body = bytearray(); base = len(out) + 4 * len(recs)
    for r in recs:
        offs.append(base + len(body) if r else 0); body += r
        while len(body) % 4: body += b'\0'
    out += struct.pack('<%dI' % len(recs), *offs) + body
    open(dst, 'wb').write(out)
    print('import_b2_sprites: %d species, %.1f MB, %s -> %s' % (max_sp, len(out) / 1e6, up.name(), dst))


if __name__ == '__main__':
    main()
