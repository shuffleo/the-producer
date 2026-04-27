# Video Art Studio Profile (Cursor)

This profile narrows OpenMontage into a practical local setup for animated film and video art work while preserving upstream compatibility.

## Studio Intent

- Primary focus: animated film, cinematic video art, and real-footage essay montage.
- Default audio direction: music-first, minimal narration.
- Style direction: custom playbooks (do not rely on stock OpenMontage house styles).

## Pipeline Scope

Use these pipelines by default:

- `animation`
- `cinematic`
- `documentary-montage`
- `hybrid` (optional, for source+generated mixed cuts)

De-prioritize for this profile unless explicitly requested:

- `clip-factory`
- `podcast-repurpose`
- `screen-demo`
- `avatar-spokesperson`
- `localization-dub`
- `talking-head`

## Runtime Governance (Required)

- Run provider/runtime preflight before production planning.
- When both Remotion and HyperFrames are available, always present both to the user and recommend one.
- Lock `render_runtime` in proposal artifacts before asset generation.
- Never silently swap runtimes after proposal.
- For `documentary-montage`, keep `render_runtime` on Remotion unless the user approves a change and the path is explicitly re-decided.

## Style Authoring Workflow

Create custom style playbooks in `styles/` by adapting existing structure, then validate.

Reference files:

- `styles/anime-ghibli.yaml`
- `styles/flat-motion-graphics.yaml`
- `schemas/styles/playbook.schema.json`
- `styles/playbook_loader.py`
- `skills/creative/animation-pipeline.md`
- `skills/meta/skill-creator.md`

Custom style minimum:

- `identity`
- `visual_language`
- `typography`
- `motion`
- `audio`
- `asset_generation`
- `overlays`
- `quality_rules`

## Session Checklist (Per Project)

1. Pick one pipeline (`animation`, `cinematic`, `documentary-montage`, or `hybrid`).
2. Run preflight (`make preflight`) and summarize available providers.
3. Propose concept options with cost and runtime shortlist.
4. Get approval before generating assets.
5. Produce canonical stage artifacts and checkpoints.
6. Archive `proposal_packet`, `scene_plan`, `edit_decisions`, and `render_report` with final output.

## Git Workflow

- Keep `origin` as personal fork and `upstream` as `calesthio/OpenMontage`.
- Avoid hard pruning upstream files; keep profile rules and studio assets additive.
- Sync from upstream regularly, then push to fork for backup.