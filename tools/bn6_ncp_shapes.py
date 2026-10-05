# Reads BN6's NaviCust program table (StructArr_813944C, data/dat36.s:379) and the 7x7 shapes it points to.
import re, sys
NAMES = ['None','SuprArmr','Custom1','Custom2','MegFldr1','MegFldr2','GigFldr1','FstBarr','Shield','Reflect','AntiDmg',
 'FlotShoe','AirShoes','UnderSht','ChpShufl','NumbrOpn','SneakRun','OilBody','Fish','Battery','Jungle','Collect',
 'Millions','Humor','Poem','SlipRunr','AutoHeal','BustPack','BodyPack','FldrPak1','FldrPak2','BugStop','Rush','Beat',
 'Tango','Attack+1','Speed+1','Charge+1','AttckMAX','SpeedMAX','ChargMAX','HP+50','HP+100','HP+200','HP+300','HP+400','HP+500']
def load(root):
    lines = open(root + '/data/dat36.s').read().split('\n')
    # flatten every labelled block into tokens: ('lab', name) markers, bytes, and ('ptr', label)
    toks = []
    for l in lines:
        l = l.split('//')[0].strip()
        m = re.match(r'^(\w+)::', l)
        if m: toks.append(('lab', m.group(1))); continue
        m = re.match(r'\.byte (.*)', l)
        if m: toks += [int(v, 0) for v in m.group(1).split(',')]; continue
        m = re.match(r'\.word (.*)', l)
        if m:
            for v in m.group(1).split(','):
                v = v.strip()
                if re.match(r'^(0x[0-9a-fA-F]+|\d+)$', v):
                    toks += list(int(v, 0).to_bytes(4, 'little'))
                else:
                    toks += [('ptr', v)] + [None] * 3
    # label -> byte offset in a flat stream
    flat = []; lab = {}
    for t in toks:
        if isinstance(t, tuple) and t[0] == 'lab': lab[t[1]] = len(flat)
        else: flat.append(t)
    return flat, lab
def entries(root):
    flat, lab = load(root)
    base = lab['StructArr_813944C']; end = lab['FlagArr_813A01C']
    out = []
    for e in range((end - base) // 16):
        b = flat[base + e * 16: base + e * 16 + 16]
        def shape(off):
            p = b[off]
            if not isinstance(p, tuple): return None
            s = lab[p[1]]; return [flat[s + i] for i in range(49)]
        out.append(dict(entry=e, prog=e >> 2, var=e & 3, group=b[0], plus=b[1], colour=b[3], bug=b[4],
                        shape=shape(8), cshape=shape(12)))
    return out
if __name__ == '__main__':
    for d in entries(sys.argv[1]):
        if d['colour'] == 0 or d['shape'] is None: continue
        n = sum(1 for v in d['shape'] if v); nc = sum(1 for v in d['cshape'] if v) if d['cshape'] else 0
        print('%-9s v%d colour=%d plus=%d group=%d bug=%2d cells=%d compressed=%d' % (NAMES[d['prog']] if d['prog'] < len(NAMES) else d['prog'], d['var'], d['colour'], d['plus'], d['group'], d['bug'], n, nc))
