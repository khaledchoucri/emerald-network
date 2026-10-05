#!/usr/bin/env python3
"""Run the same self-test battles with the old autopilot and the PKBN_BOT=smart test bot and compare them
(POC-12). Run from the host build folder.  usage: python3 tools/bot_compare.py [ids.py] [outdir]
Battle specs use species/move names; ids.py turns them into numbers (same helper the regression scripts use)."""
import os, re, subprocess, sys, concurrent.futures as cf
IDS = sys.argv[1] if len(sys.argv) > 1 else 'ids.py'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/botcmp'
P = "MUDKIP:22:WATER_GUN/TACKLE/MUD_SLAP/GROWL"
P3 = "COMBUSKEN:20:EMBER/DOUBLE_KICK/PECK/FOCUS_ENERGY|MARSHTOMP:20:WATER_GUN/MUD_SHOT/TACKLE/MUD_SLAP|GROVYLE:20:ABSORB/QUICK_ATTACK/LEER/POUND"
E = "WAILORD:45:SPLASH"
BATTLES = [
    ('x4', "TORCHIC:13:EMBER/SCRATCH/GROWL/FOCUS_ENERGY,WURMPLE:20:TACKLE", {}),
    ('x5', "MARSHTOMP:15:WATER_GUN/TACKLE/GROWL/MUD_SLAP,WAILORD:25:SPLASH", {}),
    ('x7', "MUDKIP:8:TACKLE/GROWL,GEODUDE:20:TACKLE", {}),
    ('t2', "GLOOM:30:TOXIC/POISON_POWDER/ACID/SLUDGE_BOMB,MACHOP:28:KARATE_CHOP/LOW_KICK/LEER/FOCUS_ENERGY", {}),
    ('t4', "SWELLOW:30:FLY/QUICK_ATTACK/AERIAL_ACE/ENDEAVOR|SANDSLASH:30:DIG/EARTHQUAKE/ROCK_SLIDE/SPIKES,GEODUDE:25:ROCK_THROW/MAGNITUDE/SELF_DESTRUCT/DEFENSE_CURL", {}),
    ('t6', "BRELOOM:30:MACH_PUNCH/LEECH_SEED/STUN_SPORE/SKY_UPPERCUT|MAGNETON:30:THUNDER_WAVE/LOCK_ON/ZAP_CANNON/SPARK,KOFFING:28:POISON_GAS/SMOG/SLUDGE/SELF_DESTRUCT", {}),
    ('t7', "SHARPEDO:35:CRUNCH/SURF/AGILITY/SLASH|ABSOL:35:RAZOR_WIND/BITE/SWORDS_DANCE/FUTURE_SIGHT,MAWILE:30:FAKE_TEARS/BITE/SWEET_SCENT/VICE_GRIP", {}),
    ('e1', P + ",GRAVELER:24:DIG/EARTHQUAKE/ROCK_SLIDE/ROCK_TOMB", {}),
    ('e2', P + ",JIGGLYPUFF:26:SING/REST/BODY_SLAM/ROLLOUT", {}),
    ('e3', P + ",XATU:24:FUTURE_SIGHT/CONFUSE_RAY/WISH/TELEPORT", {}),
    ('e4', P + ",PIDGEOTTO:24:FLY/GUST/WHIRLWIND/QUICK_ATTACK", {}),
    ('e5', P + ",GRIMER:24:TOXIC/POISON_GAS/SLUDGE/HARDEN", {}),
    ('p3', P3 + ",POOCHYENA:24:BITE/TACKLE/ROAR/HOWL", {}),
    ('k3', "LAPRAS:30:SURF/HYDRO_PUMP/PSYWAVE/BODY_SLAM," + E, {}),
    ('k6', "HERACROSS:30:PIN_MISSILE/ARM_THRUST/MEGAHORN/BRICK_BREAK," + E, {}),
    ('r1', "MARSHTOMP:22:WATER_GUN/MUD_SHOT/TACKLE/MUD_SLAP|TAILLOW:15:PECK/QUICK_ATTACK/GROWL/FOCUS_ENERGY,ZIGZAGOON:3:GROWL", {'PKBN_TEST_TRAINER': '265'}),
    ('w1', "MARSHTOMP:20:MUD_SHOT/WATER_GUN/MUD_SPORT/TAKE_DOWN,ZIGZAGOON:8:TACKLE/GROWL/HEADBUTT", {'PKBN_TEST_FOES': '286:7,290:6'}),
]
OUTCOME = {'1': 'won', '2': 'lost', '4': 'ran', '7': 'caught'}

def run(name, spec, env, bot):
    d = os.path.join(OUT, f'{name}-{bot}')
    os.makedirs(d, exist_ok=True)
    ids = subprocess.run(['python3', IDS, spec], capture_output=True, text=True).stdout.strip()
    e = dict(os.environ, PKBN_SELFTEST=ids, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', **env)
    if bot == 'smart':
        e['PKBN_BOT'] = 'smart'
    log = subprocess.run(['timeout', '300', './pokeemerald64'], env=e, capture_output=True, text=True, errors='replace').stdout
    open(os.path.join(d, 'log.txt'), 'w').write(log)
    m = re.search(r'outcome=(\d+)', log)
    b = re.search(r'busting: turns-clock L(\d+) \(time (-?\d+) hits (-?\d+) steps (-?\d+) chain (\d+) counters (\d+) nofaint (\d+)\), seconds-clock L(\d+).*?(\d+) frames', log)
    return dict(name=name, bot=bot, outcome=OUTCOME.get(m.group(1), m.group(1)) if m else ('timeout' if 'TIMEOUT' in log else '?'),
                turnsL=int(b.group(1)) if b else None, secsL=int(b.group(8)) if b else None,
                hits=int(b.group(3)) if b else None, steps=int(b.group(4)) if b else None,
                frames=int(b.group(9)) if b else None, chips=log.count(' uses ') )

jobs = [(n, s, e, bot) for n, s, e in BATTLES for bot in ('old', 'smart')]
with cf.ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
    res = list(ex.map(lambda j: run(*j), jobs))
by = {(r['name'], r['bot']): r for r in res}
L = lambda v: '-' if v is None else ('S' if v == 11 else str(v))
print(f"{'battle':6} | {'old: result  L(t/s) hit pts  frames':38} | {'smart: result  L(t/s) hit pts  frames':38}")
for n, _, _ in BATTLES:
    row = []
    for bot in ('old', 'smart'):
        r = by[(n, bot)]
        row.append(f"{r['outcome']:7} {L(r['turnsL']):>2}/{L(r['secsL']):<2} {('-' if r['hits'] is None else r['hits']):>4} {('-' if r['frames'] is None else r['frames']):>7}")
    print(f"{n:6} | {row[0]:38} | {row[1]:38}")
for bot in ('old', 'smart'):
    rs = [by[(n, bot)] for n, _, _ in BATTLES]
    won = [r for r in rs if r['outcome'] == 'won']
    avg = lambda k: sum(r[k] for r in won if r[k] is not None) / max(1, len([r for r in won if r[k] is not None]))
    print(f"{bot:5}: {len(won)}/{len(rs)} won; won battles avg Busting L{avg('turnsL'):.1f} (turns) L{avg('secsL'):.1f} (seconds), "
          f"hit points {avg('hits'):+.2f}, {avg('frames') / 60:.1f} s of fight")
