# Ground rules for AI-assisted work in this repo

The point of this project is to work only from the actual game code. No hallucinated mechanics.

1. **Cite or flag.** Every claim about how either game works must cite `upstream/<repo>/<path>:<line>`
   at the pinned commit (see README). Anything not yet verified is written as **UNVERIFIED** and
   is not used for design decisions until verified.
2. **upstream/ is read-only.** Never edit, format, or build in place there. Our code lives in `poc/`
   (later `src/`). Patches to the host are kept as diffs/branches of our own, not edits to upstream/.
3. **Ground truth for BN6 is the assembly** (`upstream/bn6f/asm`, `data`, `include`).
   `upstream/bn6f/docs/decomp/*.c` is machine-generated pseudo-C (Hex-Rays style) — useful for
   reading, NOT authoritative. Confirm any conclusion against the asm.
   Many BN6 functions are still unnamed (`sub_XXXXXXX`); names are community guesses.
4. **Host reference = pokeemerald-pc_port.** Use pret/pokeemerald to compare when the port
   changed something (it adds a PORTABLE build mode: hardware regions become arrays).
5. **Findings format** (research/NN-topic.md): Question → Method (what was read/run) →
   Evidence (citations, command output) → Conclusion → Open questions.
6. **No ROMs, built binaries or extracted copyrighted assets are committed or shared.**
