#!/usr/bin/env python3
"""Chip-code chain simulator (research tool, see docs/design/02-chip-codes.md).

Reads real Emerald data (battle_moves.h, contest_moves.h) and estimates how many chips a random
5-chip hand can chain under a candidate code scheme. Assumes benched Pokemon's chips can be played
(they switch in), so only codes / same-name decide chaining.

usage: python3 tools/codes_sim.py [--root upstream/pokeemerald-pc_port]
"""
import argparse, collections, random, re

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="upstream/pokeemerald-pc_port")
args = ap.parse_args()

src = open(f"{args.root}/src/data/contest_moves.h").read().replace("[MOVE_NONE] = {0},", "")
ents = re.findall(r"\[(MOVE_\w+)\]\s*=\s*\{(.*?)\n    \}", src, re.S)
bm = open(f"{args.root}/src/data/battle_moves.h").read()
mv = {n: dict(re.findall(r"\.(\w+)\s*=\s*([^,\n]+)", b)) for n, b in re.findall(r"\[(MOVE_\w+)\]\s*=\s*\{(.*?)\n    \}", bm, re.S)}

groups, suit = collections.defaultdict(set), {}
for m, b in ents:
    s = re.search(r"comboStarterId\s*=\s*(\w+)", b)
    if s and s.group(1) != "0":
        groups[m].add(s.group(1))
    suit[m] = re.search(r"contestCategory\s*=\s*(\w+)", b).group(1)
    cm = re.search(r"comboMoves\s*=\s*\{([^}]*)\}", b)
    if cm:
        for x in cm.group(1).split(","):
            x = x.strip()
            if x and x != "0":
                groups[m].add(x)

def legal(m):
    """Candidate scheme: contest-combo groups as lanes; weak (power<=50) or ungrouped moves also get their contest suit."""
    g = set(groups[m])
    if int(mv[m]["power"]) <= 50 or not g:
        g.add(suit[m])
    return sorted(g)

def copies(pp):
    pp = int(pp)
    return 3 if pp >= 30 else 2 if pp >= 15 else 1

PARTY = [["MOVE_TACKLE", "MOVE_GROWL", "MOVE_MUD_SLAP", "MOVE_WATER_GUN"],
         ["MOVE_POUND", "MOVE_LEER", "MOVE_ABSORB", "MOVE_QUICK_ATTACK"],
         ["MOVE_PECK", "MOVE_GROWL", "MOVE_QUICK_ATTACK"]]

def build(party, union):
    chips = []
    for i, moves in enumerate(party):
        for m in moves:
            L = legal(m)
            for k in range(copies(mv[m]["pp"])):
                chips.append((i, m, frozenset(L) if union else frozenset([L[k % len(L)]])))
    return chips

def best(hand):
    b = 0
    for code in set().union(*[c[2] for c in hand]):
        b = max(b, sum(1 for c in hand if code in c[2]))
    return max(b, max(collections.Counter(c[1] for c in hand).values()))

random.seed(3)
for i, moves in enumerate(PARTY):
    for m in moves:
        print(i, m[5:], [x.replace("COMBO_STARTER_", "").replace("CONTEST_CATEGORY_", "suit:") for x in legal(m)])
for label, party in (("party of 3", PARTY), ("Mudkip alone", PARTY[:1])):
    for union in (False, True):
        chips = build(party, union)
        avg = sum(best(random.sample(chips, 5)) for _ in range(4000)) / 4000
        print(f"{label:13s} {'all legal codes' if union else 'one code per copy':18s} folder={len(chips):2d} chips/turn={avg:.2f}")
