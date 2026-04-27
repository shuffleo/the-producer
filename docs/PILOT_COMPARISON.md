# Pilot Comparison - Video Art Studio

This document compares the two executed baseline pilots and locks default studio conventions for future projects.

## Pilots Executed

- Animation pilot:
  - Project: `pipeline/pilot_animation_nocturne`
  - Output: `pipeline/pilot_animation_nocturne/outputs/animation_pilot_nocturne.mp4`
  - Pipeline type: `animation`
  - Style playbook: `styles/video-art-nocturne.yaml`
  - Asset path: FAL FLUX still generation + local music fallback + local compose

- Documentary pilot:
  - Project: `pipeline/pilot_documentary_montage_nightcity`
  - Output: `pipeline/pilot_documentary_montage_nightcity/outputs/documentary_pilot_nightcity.mp4`
  - Pipeline type: `documentary-montage`
  - Asset path: public real-footage clip ingestion + local ambient music + local compose

## Outcome Summary

- The animation path is stable and efficient for your workflow because it depends primarily on `FAL_KEY` and local post.
- The documentary path is stable when source acquisition is deterministic (known URLs or curated source lists), avoiding fragile broad stock search fan-out.
- Music-first outputs work without Suno by using local ambient generation; you can optionally re-enable Suno later for richer tracks.

## Locked Conventions (v1)

1. **Provider baseline**: FAL-first for generation tasks.
2. **Audio default**: music-first, minimal narration.
3. **Runtime policy**:
   - Use Remotion-first for full pipeline proposals where runtime comparison is required.
   - Use FFmpeg compose for deterministic pilot baselines and quick validation loops.
4. **Style policy**:
   - Use custom style playbooks in `styles/`.
   - Validate each style against `schemas/styles/playbook.schema.json` before pilot runs.
5. **Artifact discipline**:
   - Archive `proposal_packet`, `scene_plan`, `asset_manifest`, `edit_decisions`, and `render_report` in each pilot project.

## Next Recommended Increment

- Add one narrative short pilot in `cinematic` using the same `video-art-nocturne` style and FAL video generation, then compare visual coherence against the animation baseline.
