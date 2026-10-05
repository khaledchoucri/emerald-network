#!/usr/bin/env python3
"""Folder memory maths (design 08): draw probabilities for BN-style folders. Exact where possible, else Monte Carlo."""
from math import comb
import random

def p_in_hand(F, c, h):
    """P(at least one of c copies among the h chips dealt from a shuffled folder of F)."""
    if c <= 0: return 0.0
    if h >= F: return 1.0
    return 1 - comb(F - c, h) / comb(F, h)

def expected_customs_to_see(F, c, h, kept_policy='use_all', trials=20000, rng=random.Random(1)):
    """Average number of Customs until a copy shows up, BN refill rule: unused chips stay, hand tops up to h,
    used chips are gone (we reshuffle the discard pile when the draw pile runs out)."""
    total = 0
    for _ in range(trials):
        pile = [1] * c + [0] * (F - c); rng.shuffle(pile)
        discard = []; hand = []; n = 0
        while True:
            n += 1
            while len(hand) < h:
                if not pile:
                    pile = discard; discard = []; rng.shuffle(pile)
                    if not pile: break
                hand.append(pile.pop())
            if 1 in hand: break
            # the player uses 2 chips per turn (typical), the rest stay in hand
            for _ in range(min(2, len(hand))):
                discard.append(hand.pop(0))
            if n > 200: break
        total += n
    return total / trials

if __name__ == '__main__':
    print('P(see at least one copy in the opening hand), folder 30, hand 5 / 6 / 7')
    for c in range(1, 6):
        print('  copies %d: %5.1f%%  %5.1f%%  %5.1f%%' % (c, 100 * p_in_hand(30, c, 5), 100 * p_in_hand(30, c, 6), 100 * p_in_hand(30, c, 7)))
    print('Average Customs until the first copy appears (folder 30, hand 5, 2 chips used per turn)')
    for c in range(1, 6):
        print('  copies %d: %.2f Customs' % (c, expected_customs_to_see(30, c, 5)))
    print('Small folders (early game, reshuffling): folder F, 1 copy, hand 5')
    for F in (4, 8, 12, 20, 30):
        print('  folder %2d: opening hand %5.1f%%, avg Customs to see it %.2f' % (F, 100 * p_in_hand(F, 1, 5), expected_customs_to_see(F, 1, 5)))

def offers_per_battle(F, c, h=5, used=2, customs=8, trials=20000, rng=random.Random(2)):
    """Average number of Customs (out of `customs`) in which at least one copy is in the hand (reshuffle on)."""
    tot = 0
    for _ in range(trials):
        pile = [1] * c + [0] * (F - c); rng.shuffle(pile); discard = []; hand = []
        for t in range(customs):
            while len(hand) < h:
                if not pile:
                    pile, discard = discard, []; rng.shuffle(pile)
                    if not pile: break
                hand.append(pile.pop())
            if 1 in hand:
                tot += 1
                hand.remove(1); discard.append(1)         # the player uses the copy...
                if hand: discard.append(hand.pop(0))      # ...and one other chip
            else:
                for _ in range(min(used, len(hand))): discard.append(hand.pop(0))
    return tot / trials

def p_code_pair(F, k, h=5):
    """P(the hand holds >= 2 chips of one code), k chips of that code in a folder of F."""
    return 1 - comb(F - k, h) / comb(F, h) - k * comb(F - k, h - 1) / comb(F, h)

def report2():
    print('Customs (of 8) where the chip is offered, used whenever offered, hand 5')
    for F in (12, 20, 30):
        print('  folder %2d: ' % F + '  '.join('%d cop %.1f' % (c, offers_per_battle(F, c)) for c in range(1, 6)))
    print('P(opening hand of 5 holds a same-code pair), k chips of the code in a folder of 30')
    print('  ' + '  '.join('k=%d %4.1f%%' % (k, 100 * p_code_pair(30, k)) for k in (3, 5, 8, 10, 15)))
    print('Dilution: one move with 1 base copy in a folder of 24, as others add copies (hand 5)')
    for F in (24, 26, 28, 30):
        print('  folder %d: %4.1f%%' % (F, 100 * p_in_hand(F, 1, 5)))

if __name__ == '__main__':
    report2()
