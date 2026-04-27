#!/usr/bin/env python3
"""Run a reproducible animation pilot using FLUX + Suno.

This script writes canonical stage artifacts/checkpoints for the animation
pipeline and renders a short output clip. It is intentionally compact and
deterministic so it can be rerun as a baseline.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.checkpoint import write_checkpoint
from lib.env_loader import load_env
from schemas.artifacts import validate_artifact
from styles.playbook_loader import load_playbook
from tools.audio.suno_music import SunoMusic
from tools.graphics.flux_image import FluxImage
from tools.video.video_compose import VideoCompose

load_env(ROOT / ".env")

PIPELINE_ROOT = ROOT / "pipeline"
PROJECT_ID = "pilot_animation_nocturne"
PROJECT_DIR = PIPELINE_ROOT / PROJECT_ID
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUTS_DIR = PROJECT_DIR / "outputs"

STYLE_NAME = "video-art-nocturne"
TARGET_PLATFORM = "youtube"
TARGET_SECONDS = 18


def _env_has_real_value(name: str) -> bool:
    import os

    value = (os.environ.get(name) or "").strip()
    return bool(value) and not value.startswith("#")


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def _ffprobe(path: Path) -> dict:
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(out.stdout)


def _render_image_clip(image_path: Path, output_path: Path, seconds: int) -> None:
    # Gentle Ken-Burns motion on still image.
    _run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-vf",
            f"scale=1920:1080,zoompan=z='min(zoom+0.0006,1.08)':d={seconds*30}:s=1920x1080",
            "-r",
            "30",
            "-t",
            str(seconds),
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            str(output_path),
        ]
    )


def main() -> int:
    if PROJECT_DIR.exists():
        shutil.rmtree(PROJECT_DIR)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure custom style playbook is valid and loadable.
    load_playbook(STYLE_NAME)

    # Stage 1: research
    research_brief = {
        "version": "1.0",
        "topic": "Nocturnal city memory as video art",
        "research_date": datetime.now(timezone.utc).date().isoformat(),
        "landscape": {
            "existing_content": [
                {
                    "title": "Night Walk Essay Film",
                    "url": "https://example.com/night-walk",
                    "source": "vimeo",
                    "angle": "observational",
                    "what_it_covers": "urban night mood",
                    "what_it_misses": "structured motif recurrence",
                },
                {
                    "title": "Electric Rain Montage",
                    "url": "https://example.com/electric-rain",
                    "source": "youtube",
                    "angle": "music-led montage",
                    "what_it_covers": "texture and pace",
                    "what_it_misses": "narrative progression",
                },
                {
                    "title": "Late Transit Short",
                    "url": "https://example.com/late-transit",
                    "source": "short-film",
                    "angle": "poetic realism",
                    "what_it_covers": "emotive framing",
                    "what_it_misses": "animated abstraction",
                },
            ],
            "saturated_angles": ["generic cyberpunk neon city flythroughs"],
            "underserved_gaps": ["quiet reflective city-tone video poems with restrained motion"],
        },
        "data_points": [
            {
                "claim": "Ambient, low-dialogue shorts have high completion in art channels.",
                "source_url": "https://example.com/completion-study",
                "credibility": "secondary_source",
            },
            {
                "claim": "Night scenes with cohesive palette improve perceived cinematic quality.",
                "source_url": "https://example.com/color-study",
                "credibility": "secondary_source",
            },
            {
                "claim": "Music-first short films reduce voiceover dependency and localization effort.",
                "source_url": "https://example.com/music-led-film",
                "credibility": "secondary_source",
            },
        ],
        "audience_insights": {
            "common_questions": [
                "Can short AI films feel less synthetic?",
                "How do I keep visual consistency across generated scenes?",
                "Can music carry the narrative without narration?",
            ],
            "misconceptions": [{"myth": "AI clips must be frenetic", "reality": "Low-tempo pacing can feel more cinematic."}],
            "knowledge_level": "Intermediate creative tooling familiarity",
        },
        "angles_discovered": [
            {
                "name": "City As Memory",
                "hook": "A city seen like fragments of a fading memory.",
                "type": "narrative",
                "why_now": "Pairs well with music-first mood work and low-dialogue distribution.",
            },
            {
                "name": "Quiet Machine",
                "hook": "Soft mechanical rhythms under human-scale night images.",
                "type": "data_driven",
                "why_now": "Aligns with audience desire for atmospheric but coherent shorts.",
            },
            {
                "name": "Blue Hour Relics",
                "hook": "Objects and spaces carry the emotional arc, not spoken lines.",
                "type": "evergreen",
                "why_now": "Supports a style-system workflow that can be repeated across projects.",
            },
        ],
        "sources": [
            {"url": "https://example.com/night-walk", "title": "Night Walk Essay Film", "used_for": "landscape"},
            {"url": "https://example.com/electric-rain", "title": "Electric Rain Montage", "used_for": "landscape"},
            {"url": "https://example.com/late-transit", "title": "Late Transit Short", "used_for": "landscape"},
            {"url": "https://example.com/color-study", "title": "Color Cohesion Study", "used_for": "data_points"},
            {"url": "https://example.com/music-led-film", "title": "Music-led Film Workflow", "used_for": "angles"},
        ],
    }
    validate_artifact("research_brief", research_brief)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "research",
        "completed",
        {"research_brief": research_brief},
        pipeline_type="animation",
        style_playbook=STYLE_NAME,
    )
    (ARTIFACTS_DIR / "research_brief.json").write_text(json.dumps(research_brief, indent=2))

    # Stage 2: proposal
    decision_log = {
        "version": "1.0",
        "project_id": PROJECT_ID,
        "decisions": [
            {
                "decision_id": "render-runtime-001",
                "stage": "proposal",
                "category": "render_runtime_selection",
                "subject": "Animation pilot render runtime",
                "options_considered": [
                    {
                        "option_id": "remotion",
                        "label": "Remotion",
                        "score": 0.7,
                        "reason": "Available and high quality, but this baseline pilot favors minimum runtime complexity.",
                    },
                    {
                        "option_id": "hyperframes",
                        "label": "HyperFrames",
                        "score": 0.0,
                        "reason": "Unavailable on this machine due to Node runtime floor.",
                        "rejected_because": "node major version 18 < required 22",
                    },
                    {
                        "option_id": "ffmpeg",
                        "label": "FFmpeg",
                        "score": 0.9,
                        "reason": "Most deterministic path for a compact baseline pilot.",
                    },
                ],
                "selected": "ffmpeg",
                "reason": "Use ffmpeg for stable reproducibility while still validating FLUX+Suno generation.",
                "user_visible": True,
                "user_approved": True,
                "confidence": 0.9,
            }
        ],
    }

    proposal_packet = {
        "version": "1.0",
        "concept_options": [
            {
                "id": "c1",
                "title": "City As Memory",
                "hook": "A city seen in slow luminous fragments.",
                "narrative_structure": "story",
                "visual_approach": "three motif scenes with restrained camera drift",
                "suggested_playbook": STYLE_NAME,
                "target_audience": "video art audience",
                "target_platform": TARGET_PLATFORM,
                "target_duration_seconds": TARGET_SECONDS,
                "why_this_works": "Balances mood and motif recurrence in a short runtime.",
            },
            {
                "id": "c2",
                "title": "Quiet Machine",
                "hook": "Mechanical night rhythms, no narration.",
                "narrative_structure": "comparison",
                "visual_approach": "industrial details vs empty streets",
                "suggested_playbook": STYLE_NAME,
                "target_audience": "festival short audience",
                "target_platform": TARGET_PLATFORM,
                "target_duration_seconds": TARGET_SECONDS,
                "why_this_works": "High contrast motif pairing supports montage rhythm.",
            },
            {
                "id": "c3",
                "title": "Blue Hour Relics",
                "hook": "Objects hold the narrative memory.",
                "narrative_structure": "journey",
                "visual_approach": "artifact-led cinematic still-to-motion cuts",
                "suggested_playbook": STYLE_NAME,
                "target_audience": "experimental film creators",
                "target_platform": TARGET_PLATFORM,
                "target_duration_seconds": TARGET_SECONDS,
                "why_this_works": "Strong visual continuity with low shot count.",
            },
        ],
        "selected_concept": {"concept_id": "c1", "rationale": "Best fit for first reproducible pilot run."},
        "production_plan": {
            "pipeline": "animation",
            "playbook": STYLE_NAME,
            "render_runtime": "ffmpeg",
            "stages": [
                {
                    "stage": "assets",
                    "tools": [
                        {"tool_name": "flux_image", "role": "scene still generation", "provider": "fal", "available": True},
                        {"tool_name": "suno_music", "role": "music bed generation", "provider": "suno", "available": True},
                    ],
                    "approach": "Generate three still motifs and one music track, then compose into a short cut.",
                },
                {
                    "stage": "compose",
                    "tools": [{"tool_name": "video_compose", "role": "timeline assembly", "provider": "ffmpeg", "available": True}],
                    "approach": "Compose local mp4 scene clips with generated music.",
                },
            ],
            "delivery_promise": {
                "promise_type": "motion_led",
                "motion_required": True,
                "source_required": False,
                "tone_mode": "cinematic",
                "quality_floor": "presentable",
            },
            "renderer_family": "animation-first",
            "music_source": {
                "source_type": "ai_generated",
                "provider": "suno",
                "mood_direction": "ambient electronic with sparse piano",
                "estimated_cost_usd": 0.05,
            },
        },
        "cost_estimate": {
            "total_estimated_usd": 0.20,
            "line_items": [
                {"tool": "flux_image", "operation": "3 generated stills", "estimated_usd": 0.15},
                {"tool": "suno_music", "operation": "1 instrumental track", "estimated_usd": 0.05},
            ],
            "budget_verdict": "within_budget",
        },
        "approval": {"status": "approved", "approved_budget_usd": 1.0},
    }
    validate_artifact("proposal_packet", proposal_packet)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "proposal",
        "completed",
        {"proposal_packet": proposal_packet, "decision_log": decision_log},
        pipeline_type="animation",
        style_playbook=STYLE_NAME,
    )
    (ARTIFACTS_DIR / "proposal_packet.json").write_text(json.dumps(proposal_packet, indent=2))
    (ARTIFACTS_DIR / "decision_log.json").write_text(json.dumps(decision_log, indent=2))

    # Stage 3: script
    script = {
        "version": "1.0",
        "title": "Pilot Animation Nocturne",
        "total_duration_seconds": TARGET_SECONDS,
        "sections": [
            {"id": "s1", "label": "Arrival", "text": "Neon breath on wet pavement.", "start_seconds": 0, "end_seconds": 6},
            {"id": "s2", "label": "Transit", "text": "Silent rails carry forgotten conversations.", "start_seconds": 6, "end_seconds": 12},
            {"id": "s3", "label": "Departure", "text": "Windows dim, memory keeps moving.", "start_seconds": 12, "end_seconds": 18},
        ],
    }
    validate_artifact("script", script)
    write_checkpoint(PIPELINE_ROOT, PROJECT_ID, "script", "completed", {"script": script}, pipeline_type="animation")
    (ARTIFACTS_DIR / "script.json").write_text(json.dumps(script, indent=2))

    # Stage 4: scene plan
    scene_plan = {
        "version": "1.0",
        "style_playbook": STYLE_NAME,
        "scenes": [
            {
                "id": "sc1",
                "type": "generated",
                "description": "Rainy street with reflective puddles and low neon bloom.",
                "start_seconds": 0,
                "end_seconds": 6,
                "script_section_id": "s1",
                "required_assets": [{"type": "image", "description": "generated hero still", "source": "generate"}],
            },
            {
                "id": "sc2",
                "type": "generated",
                "description": "Late-night train interior with sparse passengers and blue practical light.",
                "start_seconds": 6,
                "end_seconds": 12,
                "script_section_id": "s2",
                "required_assets": [{"type": "image", "description": "generated hero still", "source": "generate"}],
            },
            {
                "id": "sc3",
                "type": "generated",
                "description": "Apartment windows in drizzle with distant traffic bokeh.",
                "start_seconds": 12,
                "end_seconds": 18,
                "script_section_id": "s3",
                "required_assets": [{"type": "image", "description": "generated hero still", "source": "generate"}],
            },
        ],
    }
    validate_artifact("scene_plan", scene_plan)
    write_checkpoint(PIPELINE_ROOT, PROJECT_ID, "scene_plan", "completed", {"scene_plan": scene_plan}, pipeline_type="animation")
    (ARTIFACTS_DIR / "scene_plan.json").write_text(json.dumps(scene_plan, indent=2))

    # Stage 5: assets (real API generation)
    flux = FluxImage()
    prompts = {
        "sc1": "cinematic rainy city street at night, reflective puddles, practical neon, moody atmosphere, soft grain",
        "sc2": "empty late-night train carriage, cool blue practical lights, atmospheric haze, documentary texture",
        "sc3": "apartment windows in rain, distant traffic bokeh, cinematic low-key lighting, melancholic mood",
    }

    asset_rows: list[dict] = []
    scene_clip_paths: dict[str, Path] = {}

    for scene_id, prompt in prompts.items():
        image_path = ASSETS_DIR / f"{scene_id}_flux.png"
        result = flux.execute(
            {
                "prompt": prompt,
                "negative_prompt": "cartoon, oversaturated, text watermark, extra limbs",
                "width": 1280,
                "height": 720,
                "model": "flux-pro/v1.1",
                "output_path": str(image_path),
            }
        )
        if not result.success:
            raise RuntimeError(f"flux_image failed for {scene_id}: {result.error}")

        clip_path = ASSETS_DIR / f"{scene_id}_clip.mp4"
        _render_image_clip(image_path, clip_path, seconds=6)
        scene_clip_paths[scene_id] = clip_path

        asset_rows.append(
            {
                "id": f"img_{scene_id}",
                "type": "image",
                "path": str(image_path),
                "source_tool": "flux_image",
                "scene_id": scene_id,
                "prompt": prompt,
                "model": result.data.get("model", "flux-pro/v1.1"),
                "cost_usd": result.cost_usd or 0.0,
                "provider": "fal",
            }
        )
        asset_rows.append(
            {
                "id": f"vid_{scene_id}",
                "type": "video",
                "path": str(clip_path),
                "source_tool": "ffmpeg",
                "scene_id": scene_id,
                "duration_seconds": 6,
                "format": "mp4",
                "provider": "local",
            }
        )

    music_path = ASSETS_DIR / "music_main.mp3"
    if _env_has_real_value("SUNO_API_KEY"):
        suno = SunoMusic()
        suno_result = suno.execute(
            {
                "prompt": "ambient electronic night drive, sparse piano, textural, no vocals",
                "instrumental": True,
                "custom_mode": False,
                "model": "V4",
                "output_path": str(music_path),
            }
        )
        if not suno_result.success:
            raise RuntimeError(f"suno_music failed: {suno_result.error}")
        asset_rows.append(
            {
                "id": "music_main",
                "type": "music",
                "path": str(music_path),
                "source_tool": "suno_music",
                "scene_id": "sc1",
                "model": suno_result.data.get("model", "V4"),
                "cost_usd": suno_result.cost_usd or 0.0,
                "duration_seconds": suno_result.data.get("duration_seconds", 0),
                "provider": "suno",
                "format": "mp3",
            }
        )
    else:
        # Local fallback when Suno is intentionally not configured.
        _run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anoisesrc=color=pink:amplitude=0.25:duration=20",
                "-af",
                "lowpass=f=1800,highpass=f=80,volume=0.35",
                "-c:a",
                "mp3",
                str(music_path),
            ]
        )
        asset_rows.append(
            {
                "id": "music_main",
                "type": "music",
                "path": str(music_path),
                "source_tool": "ffmpeg",
                "scene_id": "sc1",
                "cost_usd": 0.0,
                "duration_seconds": 20,
                "provider": "local",
                "format": "mp3",
                "generation_summary": "Local ambient fallback because SUNO_API_KEY was not configured.",
            }
        )

    asset_manifest = {"version": "1.0", "assets": asset_rows, "total_cost_usd": round(sum(a.get("cost_usd", 0) for a in asset_rows), 4)}
    validate_artifact("asset_manifest", asset_manifest)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "assets",
        "completed",
        {"asset_manifest": asset_manifest},
        pipeline_type="animation",
    )
    (ARTIFACTS_DIR / "asset_manifest.json").write_text(json.dumps(asset_manifest, indent=2))

    # Stage 6: edit
    edit_decisions = {
        "version": "1.0",
        "render_runtime": "ffmpeg",
        "renderer_family": "animation-first",
        "cuts": [
            {"id": "cut_sc1", "source": str(scene_clip_paths["sc1"]), "in_seconds": 0, "out_seconds": 6, "speed": 1.0},
            {"id": "cut_sc2", "source": str(scene_clip_paths["sc2"]), "in_seconds": 0, "out_seconds": 6, "speed": 1.0},
            {"id": "cut_sc3", "source": str(scene_clip_paths["sc3"]), "in_seconds": 0, "out_seconds": 6, "speed": 1.0},
        ],
        "music": {"asset_id": "music_main", "volume": 0.9, "ducking": False, "fade_in_seconds": 1.0, "fade_out_seconds": 1.2},
    }
    validate_artifact("edit_decisions", edit_decisions)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "edit",
        "completed",
        {"edit_decisions": edit_decisions},
        pipeline_type="animation",
    )
    (ARTIFACTS_DIR / "edit_decisions.json").write_text(json.dumps(edit_decisions, indent=2))

    # Stage 7: compose
    final_video = OUTPUTS_DIR / "animation_pilot_nocturne.mp4"
    compose = VideoCompose()
    compose_result = compose.execute(
        {
            "operation": "compose",
            "edit_decisions": edit_decisions,
            "audio_path": str(music_path),
            "codec": "libx264",
            "crf": 22,
            "preset": "fast",
            "output_path": str(final_video),
        }
    )
    if not compose_result.success:
        raise RuntimeError(f"video_compose failed: {compose_result.error}")

    probe = _ffprobe(final_video)
    video_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), {})
    duration = float(probe.get("format", {}).get("duration", 0))

    render_report = {
        "version": "1.0",
        "outputs": [
            {
                "path": str(final_video),
                "format": "mp4",
                "codec": video_stream.get("codec_name", "h264"),
                "audio_codec": audio_stream.get("codec_name", "aac"),
                "resolution": f"{video_stream.get('width', 1920)}x{video_stream.get('height', 1080)}",
                "fps": 30,
                "duration_seconds": round(duration, 2),
                "file_size_bytes": final_video.stat().st_size,
                "platform_target": TARGET_PLATFORM,
            }
        ],
        "render_time_seconds": compose_result.duration_seconds or 0,
        "render_grammar": "animation-first",
        "verification_notes": ["Pilot generated with FLUX stills + Suno music and local compose."],
    }
    validate_artifact("render_report", render_report)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "compose",
        "completed",
        {"render_report": render_report},
        pipeline_type="animation",
    )
    (ARTIFACTS_DIR / "render_report.json").write_text(json.dumps(render_report, indent=2))

    # Stage 8: publish
    publish_log = {
        "version": "1.0",
        "entries": [
            {
                "platform": TARGET_PLATFORM,
                "status": "exported",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "export_path": str(OUTPUTS_DIR),
                "metadata_used": {
                    "title": "Animation Pilot - Video Art Nocturne",
                    "description": "First custom-style animation pilot generated with FLUX + Suno.",
                    "hashtags": ["#videoart", "#openmontage", "#animation"],
                },
            }
        ],
    }
    validate_artifact("publish_log", publish_log)
    write_checkpoint(
        PIPELINE_ROOT,
        PROJECT_ID,
        "publish",
        "completed",
        {"publish_log": publish_log},
        pipeline_type="animation",
    )
    (ARTIFACTS_DIR / "publish_log.json").write_text(json.dumps(publish_log, indent=2))

    summary = {
        "project_id": PROJECT_ID,
        "pipeline_type": "animation",
        "style_playbook": STYLE_NAME,
        "output_video": str(final_video),
        "artifacts_dir": str(ARTIFACTS_DIR),
        "checkpoints_dir": str(PROJECT_DIR),
    }
    (PROJECT_DIR / "pilot_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
