# Lyric-Driven Audio Segmentation for OpenMontage

> Tool: `lyric_segmenter` | Provider: FFmpeg | Cost: free (local)
> Companion Layer 3 skill: `.agents/skills/ffmpeg/`

## Quick Reference Card

```
TOOL NAME:        lyric_segmenter
INPUT:            audio_path + structured JSON segments array
OUTPUT:           per-segment audio files + segment_manifest.json
MAX SEGMENT:      15s (Seedance default; configurable via max_segment_duration)
OUTPUT FORMATS:   wav (default), mp3, aac, flac
COST:             $0.00 (local FFmpeg)
KEY RULE:         YOU must parse the user's freeform text into canonical JSON
                  before calling this tool. The tool does NOT parse raw text.
```

## Your Job: Parse Before Calling

The user's lyrics+timestamps text will be **unstructured and different every time**.
It is your responsibility to convert it into the tool's canonical `segments` JSON
array before making the tool call. The tool only accepts clean structured JSON.

### Step-by-Step

1. **Read the user's raw text.** It may use `MM:SS`, `HH:MM:SS`, `M:SS`, or
   decimal seconds. Timestamps may be on their own lines, inline with lyrics,
   or mixed. Segment boundaries may be numbered, separated by blank lines,
   delimited by dashes, or indicated by headers.

2. **Identify segments.** Each segment has a start time, an end time, and one or
   more lyric/cue lines with intermediate timestamps. Segments may intentionally
   overlap -- this is normal for continuity between adjacent video clips.

3. **Convert all timestamps to decimal seconds.**
   - `00:08` -> `8.0`
   - `01:14` -> `74.0`
   - `1:02`  -> `62.0`
   - `01:05:30` -> `3930.0`

4. **Construct the canonical JSON.** Build a `segments` array where each item has:
   - `segment_number` (int, 1-indexed)
   - `start_seconds` (float) -- the earliest timestamp in the segment
   - `end_seconds` (float) -- the latest timestamp in the segment
   - `cues` (array) -- each lyric/SFX line with its absolute `timestamp_seconds`

5. **Validate before calling.**
   - Every `start_seconds < end_seconds`.
   - Every segment duration is within `max_segment_duration` (default 15s).
   - If any segment exceeds the limit, flag it to the user before proceeding.

6. **Call `lyric_segmenter`** with `audio_path`, `segments`, and optional
   `output_dir` / `output_format`.

## Canonical Segment Schema

```json
{
  "segment_number": 1,
  "start_seconds": 0.0,
  "end_seconds": 14.0,
  "cues": [
    {"timestamp_seconds": 0.0, "text": "Animal noise"},
    {"timestamp_seconds": 0.0, "text": "\u65e5\u982d \u540c\u591c\u665a\u4ea4\u63a5 \u5765\u4e00\u523b\u3002"}
  ]
}
```

## Worked Example

### User input (freeform)

```
Time Split:

1
00:00
Animal noise
Hello world
00:14

2
00:08
Hello world
00:13
Second verse here
00:18
Third line
00:23
```

### Your parsed JSON

```json
[
  {
    "segment_number": 1,
    "start_seconds": 0.0,
    "end_seconds": 14.0,
    "cues": [
      {"timestamp_seconds": 0.0, "text": "Animal noise"},
      {"timestamp_seconds": 0.0, "text": "Hello world"}
    ]
  },
  {
    "segment_number": 2,
    "start_seconds": 8.0,
    "end_seconds": 23.0,
    "cues": [
      {"timestamp_seconds": 8.0, "text": "Hello world"},
      {"timestamp_seconds": 13.0, "text": "Second verse here"},
      {"timestamp_seconds": 18.0, "text": "Third line"}
    ]
  }
]
```

Note: Segment 2 is 15s (23 - 8), right at the Seedance limit. If it were 16s,
warn the user.

### Tool call

```python
lyric_segmenter.execute({
    "audio_path": "assets/audio/song.wav",
    "segments": [... the JSON above ...],
    "output_dir": "output/segments",
    "output_format": "wav",
    "max_segment_duration": 15
})
```

## How Cue Timestamps Work

Each cue's `timestamp_seconds` is the **absolute position in the source audio**
where that lyric/cue occurs. It is NOT relative to the segment start.

In the user's freeform text, the pattern is typically:

```
<timestamp>
<lyric line(s) that start at that timestamp>
<next timestamp>
<lyric line(s) that start at that timestamp>
...
```

When multiple lyric lines appear between two timestamps, they all share the
earlier timestamp. The first timestamp in a segment is the start; the last
timestamp is the end. Lyric lines between the last cue timestamp and the
segment end timestamp have no spoken content at that point (the segment end
is purely a time boundary).

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Timestamps in `MM:SS` vs `M:SS` vs `HH:MM:SS` | Always normalize to decimal seconds |
| Overlapping segments | Intentional for clip continuity -- do not de-duplicate or trim |
| Non-lyric cues: "(chanting chorus)", "Animal noise" | Valid cue text -- preserve as-is |
| Segment exceeds 15s | Warn the user; they may want to re-split or accept it |
| Header lines like "Time Split:" | Strip before parsing; not a segment |
| Empty lines between segments | Use as segment delimiters, not content |
| User gives timestamps inline: "Hello world [00:14]" | Extract timestamp, keep text |

## Output

The tool writes to `output_dir`:

- `segment_01.wav`, `segment_02.wav`, ... -- one audio clip per segment
- `segment_manifest.json` -- full manifest with enriched segment data

The manifest is the downstream input for Seedance video generation, scene
planning, and storyboard workflows. Each segment's `cues` array carries the
lyric context needed for visual prompt generation.
