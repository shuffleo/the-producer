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

**Editing layer:** DaVinci Resolve Studio (via MCP server for AI-assisted workflows, or manual UI for hands-on editing).

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

## Video Editing — DaVinci Resolve

DaVinci Resolve Studio is the primary NLE (non-linear editor) for this studio. The DaVinci Resolve MCP server is installed and configured for Cursor, enabling AI-assisted editing workflows.

### Setup

- **MCP server:** `davinci-resolve-mcp` (compound mode, 27 tools)
- **Config:** `~/.cursor/mcp.json`
- **Skill reference:** `.agents/skills/davinci-resolve/SKILL.md`
- **Rule:** `.cursor/rules/davinci-resolve.mdc`

### Capabilities via MCP

- Project and timeline management (create, import, export)
- Media pool operations (import clips, audio, images)
- Timeline editing (append, trim, markers, tracks)
- Color grading (CDL, LUTs, node graphs, color groups)
- Fusion compositions (node-based VFX)
- Render pipeline (settings, presets, queue, export)

### Requirement

DaVinci Resolve Studio must be running with **External scripting set to Local** (Preferences > General).

## Video Production Tool Routing

See `AGENT_GUIDE.md` > "Video Tool Routing — Resolve vs Remotion" for the canonical routing table.

## Session Checklist (Per Project)

1. Pick one pipeline (`animation`, `cinematic`, `documentary-montage`, or `hybrid`).
2. Run preflight (`make preflight`) and summarize available providers.
3. Propose concept options with cost and runtime shortlist.
4. Get approval before generating assets.
5. Produce canonical stage artifacts and checkpoints.
6. Archive `proposal_packet`, `scene_plan`, `edit_decisions`, and `render_report` with final output.

## External Dependencies


| Tool                | Location                                     | Purpose                                                                          |
| ------------------- | -------------------------------------------- | -------------------------------------------------------------------------------- |
| DaVinci Resolve MCP | `/Users/shuffleo/Github/davinci-resolve-mcp` | Video editing via MCP                                                            |
| fal.ai              | API (FAL_KEY in `.env`)                      | AI image + video generation (Recraft, Nano Banana, GPT Image 2, Kling, Seedance) |


## Git Workflow

- Keep `origin` as personal fork and `upstream` as `calesthio/OpenMontage`.
- Avoid hard pruning upstream files; keep profile rules and studio assets additive.
- Sync from upstream regularly, then push to fork for backup.

