#!/usr/bin/env python3
"""How big should the folder be with a party of n? (design 08 §10). Monte Carlo over Emerald's real battle mix.

Model (all TUNE, stated in the doc):
  - Battle: m enemy Pokemon. Wild: m = 1. Trainers: m drawn from Emerald's trainer party sizes
    (src/data/trainer_parties.h: 1:305, 2:318, 3:135, 4:36, 5:25, 6:35 parties). Mix: 70% wild, 30% trainer.
  - K damaging chip uses knock out one enemy (Gen 3 damage at equal level: ~2-4 hits, + misses/status -> K=4).
  - The player uses up to U=2 chips per Custom. Chips of the Pokemon in battle are used directly; a benched
    Pokemon's chip switches it in (design 01). A Custom with no usable chip is a DEAD Custom (buster only).
  - The Pokemon in battle faints after S ~ U[3,6] Customs on the field (the enemy hits back); its chips leave the
    deck and hand (best case for the player), the next Pokemon with the most chips comes in.
  - No reshuffle: copies are stamina (design 08 §9 option b). A deck that runs out stops drawing (buster only);
    we count that battle as RUN-DRY.
Designs:
  shared(F, lead): one deck of F chips; the lead owns `lead` of them, the rest are split evenly over the bench.
  personal(P, bench): each Pokemon has its own deck of P chips; the hand draws H from the active Pokemon's deck,
                      plus 1 "bench slot" from a mixed deck of `bench` chips per benched Pokemon.
"""
import random

TRAINER_SIZES = [1] * 305 + [2] * 318 + [3] * 135 + [4] * 36 + [5] * 25 + [6] * 35
H, U, K = 5, 2, 4

def battle_size(rng):
    return 1 if rng.random() < 0.7 else rng.choice(TRAINER_SIZES)

def run_shared(n, F, lead, rng, key_copies=None):
    # owner of each chip; key = one of the lead's moves with key_copies copies (tracked for copy value)
    counts = [lead] + [(F - lead) // (n - 1) + (1 if i < (F - lead) % (n - 1) else 0) for i in range(n - 1)] if n > 1 else [F]
    deck = []
    for o, c in enumerate(counts):
        deck += [(o, False)] * c
    if key_copies:
        for i in range(key_copies):
            deck[i] = (0, True)
    rng.shuffle(deck)
    return deck, counts

def simulate(design, n, trials=4000, seed=1, key_copies=0):
    rng = random.Random(seed)
    tot = dict(customs=0, dead=0, forced=0, dry=0, battles=0, key_offer=0, key_customs=0, drawn=0, size=0)
    for _ in range(trials):
        m = battle_size(rng)
        alive = [True] * n
        if design[0] == 'shared':
            F, lead = design[1], design[2](n)
            deck, counts = run_shared(n, F, lead, rng, key_copies)
            size = F
            bench_deck = None
        else:
            P, bench = design[1], design[2]
            decks = []
            for o in range(n):
                d = [(o, o == 0 and i < key_copies) for i in range(P)]
                rng.shuffle(d); decks.append(d)
            bench_pool = {o: [(o, False)] * bench for o in range(1, n)}
            size = P * n
            bench_deck = None
        active, onfield, life = 0, 0, rng.randint(3, 6)
        hand, discard = [], []
        hp_left, enemies = K, m
        customs = dead = forced = 0; dry = False; drawn = 0; bench_slot = None
        while enemies > 0 and customs < 80:
            customs += 1
            # refill
            if design[0] == 'shared':
                while len(hand) < H:
                    if not deck:
                        dry = True; break
                    c = deck.pop(); drawn += 1
                    if alive[c[0]]: hand.append(c)
            else:
                d = decks[active]
                hand = [c for c in hand if c[0] == active]  # a switch redraws from the new active's deck
                while len(hand) < H:
                    if not d:
                        dry = True; break
                    hand.append(d.pop()); drawn += 1
                if bench_slot is None or not alive[bench_slot[0]] or bench_slot[0] == active:
                    pool = [c for o, cs in bench_pool.items() if alive[o] and o != active for c in cs]
                    bench_slot = rng.choice(pool) if pool else None
            if design[0] == 'personal' or True:
                if active == 0:
                    tot['key_customs'] += 1
                    if any(c[1] for c in hand): tot['key_offer'] += 1
            own = [c for c in hand if c[0] == active]
            used = 0
            if not own:
                bench = [c for c in hand if c[0] != active and alive[c[0]]]
                if design[0] == 'personal' and bench_slot is not None:
                    bench = [bench_slot]
                if not bench:
                    dead += 1
                else:
                    forced += 1
                    c = bench[0]
                    if c in hand: hand.remove(c)
                    else: bench_pool[c[0]].remove(c); bench_slot = None
                    active = c[0]; life = rng.randint(3, 6); used = 1
                    hp_left -= 1
                    own = [x for x in hand if x[0] == active]
            for c in own[:U - used]:
                hand.remove(c); discard.append(c) if False else None; hp_left -= 1; used += 1
            if hp_left <= 0:
                enemies -= 1; hp_left = K
            life -= 1
            if life <= 0 and enemies > 0:
                alive[active] = False
                hand = [c for c in hand if c[0] != active]
                cand = [o for o in range(n) if alive[o]]
                if not cand: break
                active = cand[0]; life = rng.randint(3, 6)
        tot['customs'] += customs; tot['dead'] += dead; tot['forced'] += forced; tot['dry'] += dry
        tot['battles'] += 1; tot['drawn'] += drawn; tot['size'] += size
    b = tot['battles']
    return dict(customs=tot['customs'] / b, dead=tot['dead'] / tot['customs'], forced=tot['forced'] / tot['customs'],
                dry=tot['dry'] / b, seen=tot['drawn'] / tot['size'],
                key=tot['key_offer'] / max(1, tot['key_customs']))

def copy_value(design, n):
    a = simulate(design, n, key_copies=1, seed=7)['key']
    b = simulate(design, n, key_copies=5, seed=7)['key']
    return (b - a) / 4

DESIGNS = {
    'A  shared 30, lead 30-5(n-1)': ('shared', 30, lambda n: 30 - 5 * (n - 1)),
    'B  shared 30+5(n-1), lead 30':  None,  # F depends on n: handled below
    'B2 shared 30+5(n-1), even':     None,
    'C  personal 15 + bench slot 5': ('personal', 15, 5),
    'C2 personal 20 + bench slot 5': ('personal', 20, 5),
}

if __name__ == '__main__':
    print('n = party size. dead = Customs with nothing usable; forced = Customs where only a benched chip was usable')
    print('(you had to switch); dry = battles that ran the deck out; seen = share of the folder drawn per battle;')
    print('copy = how much ONE extra copy of the lead\'s key move raises its chance to be in a Custom hand.\n')
    for name in DESIGNS:
        print(name)
        for n in (1, 2, 3, 4, 6):
            if name.startswith('B '):
                d = ('shared', 30 + 5 * (n - 1), lambda n: 30)
            elif name.startswith('B2'):
                d = ('shared', 30 + 5 * (n - 1), lambda n, F=30 + 5 * (n - 1): F // n + F % n)
            else:
                d = DESIGNS[name]
            if d[0] == 'shared' and d[2](n) < 1:
                continue
            r = simulate(d, n)
            print('  n=%d  size %3d  customs %4.1f  dead %4.1f%%  forced %4.1f%%  dry %4.1f%%  seen %3.0f%%  copy +%4.1f pts'
                  % (n, d[1] if d[0] == 'shared' else d[1] * n, r['customs'], 100 * r['dead'], 100 * r['forced'],
                     100 * r['dry'], 100 * r['seen'], 100 * copy_value(d, n)))

def depth_table():
    """Personal folders: how big must one Pokemon's folder be so it doesn't run dry while it's on the field?"""
    global battle_size
    import random as _r
    keep = battle_size
    print('\nDepth: personal folder P, battles vs m enemies. Normal = it faints after 3-6 Customs; '
          'sweeper = it never faints (one Pokemon beats the whole team). Cells: battles where someone ran dry')
    for P in (10, 15, 20, 25, 30):
        row = []
        for m in (1, 3, 6):
            battle_size = lambda rng, m=m: m
            a = simulate(('personal', P, 5), 6, trials=2000)
            row.append('m=%d dry %3.0f%%' % (m, 100 * a['dry']))
        battle_size = keep
        print('  P=%2d  normal: %s' % (P, '  '.join(row)))
    # sweeper: closed form, the lead alone uses all m*K chips: drawn = H + m*K - U
    for P in (15, 20, 25, 30):
        print('  P=%2d  sweeper: ' % P + '  '.join('m=%d %s' % (m, 'dry' if H + m * K - U > P else 'ok (%d drawn)' % (H + m * K - U)) for m in (1, 2, 3, 4, 5, 6)))

if __name__ == '__main__':
    depth_table()
