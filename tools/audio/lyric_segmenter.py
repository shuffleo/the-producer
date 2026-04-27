"""Lyric-driven audio segmenter.

Splits a source audio file into numbered segments based on a structured
JSON array of time ranges and lyric cues.  Each segment is extracted via
FFmpeg stream-copy and a manifest JSON is written alongside the clips.

The agent is responsible for parsing the user's freeform text into the
canonical ``segments`` JSON array before calling this tool.  See the
companion skill ``skills/creative/lyric-segmentation-usage.md``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ResumeSupport,
    ToolResult,
    ToolStability,
    ToolTier,
)


class LyricSegmenter(BaseTool):
    name = "lyric_segmenter"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "audio_processing"
    provider = "ffmpeg"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "Install FFmpeg: https://ffmpeg.org/download.html\n"
        "Windows: winget install FFmpeg\n"
        "macOS: brew install ffmpeg\n"
        "Linux: sudo apt install ffmpeg"
    )
    agent_skills = ["ffmpeg", "lyric-segmentation"]

    capabilities = ["lyric_segment", "audio_split", "segment_manifest"]

    input_schema = {
        "type": "object",
        "required": ["audio_path", "segments"],
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to the source audio file.",
            },
            "segments": {
                "type": "array",
                "description": (
                    "Canonical segment list. The agent must parse the user's "
                    "freeform lyrics/timestamps text into this structure before "
                    "calling the tool."
                ),
                "items": {
                    "type": "object",
                    "required": ["segment_number", "start_seconds", "end_seconds", "cues"],
                    "properties": {
                        "segment_number": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "1-indexed segment number.",
                        },
                        "start_seconds": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Clip start in the source audio (seconds).",
                        },
                        "end_seconds": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Clip end in the source audio (seconds).",
                        },
                        "cues": {
                            "type": "array",
                            "description": "Lyric/SFX lines with absolute timestamps.",
                            "items": {
                                "type": "object",
                                "required": ["timestamp_seconds", "text"],
                                "properties": {
                                    "timestamp_seconds": {
                                        "type": "number",
                                        "description": "Absolute time in the source audio.",
                                    },
                                    "text": {
                                        "type": "string",
                                        "description": "Lyric line or cue description.",
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "output_dir": {
                "type": "string",
                "description": (
                    "Directory for segment files and manifest. "
                    "Defaults to a 'segments/' folder next to the audio file."
                ),
            },
            "output_format": {
                "type": "string",
                "enum": ["wav", "mp3", "aac", "flac"],
                "default": "wav",
                "description": "Audio format for output segments.",
            },
            "max_segment_duration": {
                "type": "number",
                "default": 15,
                "description": (
                    "Maximum allowed segment duration in seconds. "
                    "Segments exceeding this produce a warning (Seedance limit is 15s)."
                ),
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["FFmpeg error"])
    resume_support = ResumeSupport.FROM_START
    idempotency_key_fields = ["audio_path", "segments"]
    side_effects = ["writes audio segment files and manifest JSON to output_dir"]
    user_visible_verification = [
        "Play each segment clip to verify cut points align with lyrics"
    ]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        try:
            result = self._run(inputs)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _run(self, inputs: dict[str, Any]) -> ToolResult:
        segments = inputs["segments"]
        if not segments:
            return ToolResult(success=False, error="No segments provided")

        audio_path = Path(inputs["audio_path"])
        if not audio_path.exists():
            return ToolResult(
                success=False, error=f"Audio file not found: {audio_path}"
            )

        output_dir = Path(
            inputs.get("output_dir")
            or str(audio_path.parent / "segments")
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        fmt = inputs.get("output_format", "wav")
        max_dur = inputs.get("max_segment_duration", 15)

        validation_error = self._validate_segments(segments)
        if validation_error:
            return ToolResult(success=False, error=validation_error)

        warnings: list[str] = []
        enriched: list[dict[str, Any]] = []
        artifacts: list[str] = []

        for seg in segments:
            num = seg["segment_number"]
            ss = seg["start_seconds"]
            es = seg["end_seconds"]
            dur = round(es - ss, 3)

            if dur > max_dur:
                warnings.append(
                    f"Segment {num}: {dur}s exceeds max {max_dur}s"
                )

            out_name = f"segment_{num:02d}.{fmt}"
            out_path = output_dir / out_name

            self._split_segment(audio_path, ss, es, out_path, fmt)

            enriched.append({
                **seg,
                "duration_seconds": dur,
                "audio_path": str(out_path),
            })
            artifacts.append(str(out_path))

        manifest = {
            "source_audio": str(audio_path),
            "total_segments": len(enriched),
            "max_segment_duration": max_dur,
            "segments": enriched,
        }
        manifest_path = output_dir / "segment_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        artifacts.append(str(manifest_path))

        return ToolResult(
            success=True,
            data={
                "segments": enriched,
                "manifest_path": str(manifest_path),
                "warnings": warnings,
            },
            artifacts=artifacts,
        )

    def _validate_segments(self, segments: list[dict]) -> str | None:
        """Return an error message if the segments array is malformed."""
        for i, seg in enumerate(segments):
            label = f"segments[{i}]"
            if "segment_number" not in seg:
                return f"{label}: missing 'segment_number'"
            if "start_seconds" not in seg or "end_seconds" not in seg:
                return f"{label}: missing 'start_seconds' or 'end_seconds'"
            if seg["start_seconds"] >= seg["end_seconds"]:
                return (
                    f"{label}: start_seconds ({seg['start_seconds']}) "
                    f"must be less than end_seconds ({seg['end_seconds']})"
                )
            if "cues" not in seg or not seg["cues"]:
                return f"{label}: missing or empty 'cues'"
            for j, cue in enumerate(seg["cues"]):
                if "timestamp_seconds" not in cue or "text" not in cue:
                    return (
                        f"{label}.cues[{j}]: must have "
                        "'timestamp_seconds' and 'text'"
                    )
        return None

    def _split_segment(
        self,
        audio_path: Path,
        start: float,
        end: float,
        output_path: Path,
        fmt: str,
    ) -> None:
        """Extract a time range from the source audio via FFmpeg."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(audio_path),
            "-ss", str(start),
            "-to", str(end),
        ]
        if fmt == "wav":
            cmd.extend(["-c", "copy"])
        elif fmt == "mp3":
            cmd.extend(["-c:a", "libmp3lame", "-q:a", "2"])
        elif fmt == "aac":
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        elif fmt == "flac":
            cmd.extend(["-c:a", "flac"])
        else:
            cmd.extend(["-c", "copy"])
        cmd.append(str(output_path))
        self.run_command(cmd)
