# Pokémon × Battle Network — merge project

Hobby R&D project: Pokémon Emerald's overworld/party/data loop with a Mega Man
Battle Network–style real-time grid battle replacing Emerald's turn-based battles.

## Layout

```
upstream/                 READ-ONLY reference code (never edit; see CLAUDE.md)
  pokeemerald/            pret decompilation of Pokémon Emerald (C) — canonical reference
  pokeemerald-pc_port/    Kurausukun's native SDL2 port of pokeemerald — planned HOST
  bn6f/                   dism-exe disassembly of MMBN6 Cybeast Falzar (ARM/Thumb asm)
  dism-exe-notes/         dism-exe project notes on the BN disassemblies
research/                 findings, each backed by file:line citations into upstream/
poc/                      our proof-of-concept code (patches/ = our changes to the host; POC-N.md = test plans)
scripts/                  setup_host.sh: builds the patched host inside WSL
docs/                     design docs (written only from verified research)
```

## Pinned upstream commits (shallow clones)

| Repo | Branch | Commit |
|---|---|---|
| github.com/pret/pokeemerald | master | 731ad5bfd6e6f265508d0efcca0ba42f9dcf5881 |
| github.com/Kurausukun/pokeemerald | pc_port | 116582559947f4c9fbd5cdfd601f258b553661d5 |
| github.com/dism-exe/bn6f | master | d57c1968d27452de1042eff78b5dfbf124922666 |
| github.com/dism-exe/dism-exe-notes | default | (shallow, latest at setup 2026-10-04) |

## Building (verified 2026-10-04 on Ubuntu 24.04, see research/00-baseline.md)

All builds need Linux — on Windows use WSL.

- **Emerald PC port (Linux):** `sudo apt install build-essential libpng-dev libsdl2-dev`, then
  `cd upstream/pokeemerald-pc_port && make linux -j$(nproc)` → `pokeemerald64`.
  Windows .exe: see `upstream/pokeemerald-pc_port/INSTALL_PC.md` (`make winwsl`, mingw + SDL2 2.0.16).
- **bn6f (GBA ROM):** see `upstream/bn6f/INSTALL.md` (needs luckytyphlosion/agbcc
  `new_layout_with_libs`). Builds a matching ROM (`make compare` → OK) from the repo alone.

Do not build inside `upstream/` on the Windows-mounted folder if you can avoid it — copy or
build from a WSL-native path (much faster, and keeps upstream/ clean).

Built ROMs/executables are never committed (see .gitignore).
