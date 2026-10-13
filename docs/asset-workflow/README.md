# Shared game asset workflow

This folder is the durable handoff between the implementation agent overseeing
Emerald Network and Codex using image generation. Both agents read this document,
the queue, and the selected request before working. Chat can initiate work, but
accepted requirements, feedback, and delivery details belong in the request file.

## Responsibilities

**Implementation agent:** owns game design, priorities, technical constraints,
asset requests, conversion to engine formats, code integration, and in-game tests.
Provide a precise brief and actual references before marking a request ready.
Resolve gameplay and pipeline questions from the code rather than guessing.

**Codex asset agent:** owns interpreting the brief, generating and revising images
with the image generation tool, inspecting results, and documenting the delivery.
Inspect supplied local reference images before editing. Preserve transparency
unless the request changes it. Use transparent output for cutouts. Use the image
generation tool for image edits; do not substitute programmatic image editing
unless the user explicitly requests it. Keep revisions consistent with the
accepted reference and record limitations candidly.

Codex does not change gameplay, invent engine constraints, or integrate assets
unless separately requested. The implementation agent does not label a delivery
accepted until the intended use has been checked in the game. Neither agent may
treat a suggested design choice as a user decision.

## Shared files and synchronization

- `QUEUE.md`: small index of requests, priority, owner, and current state.
- `REQUEST_TEMPLATE.md`: copy to `requests/ASSET-001-short-name.md` for each asset
  or tightly related batch. Use unique, stable IDs and repository-relative paths.
- Delivery files: use `poc/assets/generated/<ID>/v001/` and increase the revision
  for each new attempt. Include the paths in the request. Keep raw outputs and
  accepted revisions; never silently replace a reviewed file.

These are Git files, not a live messaging service. Each agent must receive the
latest files through the user's normal repository sync before acting. Local edits
are not visible to an agent in another checkout until transferred. Commit/push
only when authorized by the user or the established workflow; otherwise report
the changed files for transfer. Do not reset, overwrite, or stash someone else's
work. Read the latest request immediately before updating it and preserve edits.
If concurrent edits conflict, reconcile requirements before generating.

No automatic polling or background generation is implied. When asked to work the
queue, Codex takes the highest-priority `ready` request assigned to Codex, breaking
ties by ID. The implementation agent prepares requests; Codex generates only when
the user has initiated asset work. The initial queue is intentionally empty.

## Request lifecycle

1. **draft** — implementation agent fills the template. Include a concrete visual
   brief, intended use, technical target, references, and acceptance criteria.
2. **ready** — implementation agent confirms the brief is actionable. For production
   assets, dimensions, format, transparency, and integration target are required.
   For concept exploration, mark engine constraints `not applicable` and define
   the decision the concept should help make.
3. **in_progress** — Codex records ownership and the brief revision before generating.
   Start with one strong candidate unless a specific variant count is requested.
   For a large batch, establish one reviewed sample before scaling it up.
4. **delivered** — Codex records exact files, actual properties, prompt, references,
   checks performed, and limitations. Delivery means available for review.
5. **revision_requested** — reviewer provides one consolidated, specific change list,
   distinguishing required fixes from preferences. Codex creates a new revision.
6. **accepted** — implementation agent records the chosen revision, visual review,
   integration location, and functional validation. **cancelled** closes unused work.

Use **blocked** for a missing required input or unavailable capability. Record the
missing item and responsible agent. Ask only for information that prevents useful
work; proceed on independent requests. Record harmless assumptions explicitly.
Update the request and queue together at every state transition. Keep previous
briefs/deliveries identifiable; a changed brief needs a new revision number.

## Visual and technical contract

Read `docs/design/05-visuals.md` and relevant POC documentation as context. That
document describes a 264×176 battle canvas, 44×26 panels, and 64×64 Emerald fighter
sprites. These are documented context, not universal asset dimensions. The
implementation agent must confirm the current integration target from code.
Do not assume an arbitrary PNG can replace code-drawn or runtime-decoded art.

Specify composition, camera, facing direction, silhouette, lighting, palette,
outline treatment, occupied area, anchor point, padding, and transparency where
relevant. For animations specify frame count, frame size, ordering, timing, loop
behavior, and sheet layout. For UI, specify safe areas and which labels the engine
will render; prefer engine-rendered text for small game UI unless asked otherwise.

Image generation can produce useful source art and concepts, but exact pixel
grids, palette limits, dimensions, and animation continuity must be checked rather
than promised. Never claim an output is engine-ready solely because its prompt
requested those constraints. Report actual dimensions and alpha properties when
inspectable, and mark anything unchecked. If resizing, palette conversion, sprite
packing, or cleanup remains necessary, explicitly assign it to the implementation
agent. Do not invent an exporter or change the game's pipeline to hide a mismatch.

Review source art visually for brief compliance, framing, stray elements, and
consistency. The implementation agent checks readability at native resolution,
transparency edges, anchors, palettes, sheet geometry, animation, and performance
in the actual renderer. A preview or an open image is not an integration test.

## References and provenance

Keep `CLAUDE.md` rules intact. Do not commit or share ROMs, binaries, or extracted
copyrighted game assets. Refer to restricted local references by path without
copying them into this folder or a delivery. Use permitted project screenshots
and user-provided references as appropriate; do not assume a path exists on both
machines. If the image tool cannot access a necessary reference, request that it
be attached or made available through the normal handoff.

Record reference paths and their role (style, composition, palette, etc.), the
generation prompt and tool, brief revision, output version, and review decisions.
Never store credentials or private chat dumps. Claims about original game
mechanics require pinned source citations under the repository rules; unverified
claims must be flagged. Creative proposals are labeled proposals.

## Completion report

Each agent reports the request ID, state, changed files, delivered revision, checks
actually performed, and the next responsible action. Codex reports remaining
conversion/integration work explicitly. Do not claim sync, publication, or game
acceptance without evidence.
