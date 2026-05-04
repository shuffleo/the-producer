# Production Crew

A personal AI-assisted video production studio, built on [Cursor](https://cursor.com) agents. Forked from [OpenMontage](https://github.com/calesthio/OpenMontage).

## What this is

An agentic workflow for creating videos — from concept to final render. The agent handles research, asset generation, prompt engineering, and can control DaVinci Resolve for editing. You direct.

## Stack


| Layer                       | Tools                                                          |
| --------------------------- | -------------------------------------------------------------- |
| **Agent**                   | Cursor (with MCP servers)                                      |
| **Image generation**        | Recraft V4, Nano Banana 2, GPT Image 2 (via fal.ai)            |
| **Video generation**        | Kling v3/O3, Seedance 2.0 (via fal.ai)                         |
| **Video editing (Route A)** | DaVinci Resolve **Studio** (via MCP) — full NLE with color, audio, Fusion |
| **Video editing (Route B)** | Remotion + HyperFrames + FFmpeg — code-based, no NLE needed    |
| **Audio**                   | ElevenLabs, Suno, Piper TTS, ACE-Step                          |


## Setup

```bash
git clone https://github.com/shuffleo/production-crew.git
cd production-crew
make setup
```

### API keys

Add to `.env` (all optional — more keys = more tools):

```bash
FAL_KEY=your-key              # Image + video generation (Recraft, Kling, Seedance, Nano Banana, GPT Image 2)
ELEVENLABS_API_KEY=your-key   # Voice, music, sound effects
OPENAI_API_KEY=your-key       # GPT Image 2 direct, TTS
```

### DaVinci Resolve — Route A (optional)

```bash
cd ~/Github
git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
cd davinci-resolve-mcp
python install.py --clients cursor
```

Requires **DaVinci Resolve Studio** (the free edition does not support external scripting). In Resolve 20+, scripting is enabled by default — no preferences toggle needed.

## Project structure

```
production-crew/
├── .agents/skills/        # 64 agent skills (canonical location)
├── .cursor/rules/         # Cursor rules (davinci-resolve, video-art-studio, openmontage)
├── docs/                  # Studio profile, architecture
├── projects/              # Per-project folders (git-ignored)
│   └── <project-name>/   # Each project has its own assets, prompts, and videos
├── tools/                 # Python tool registry
├── skills/                # Pipeline stage directors
├── pipeline_defs/         # Pipeline YAML manifests
└── AGENT_GUIDE.md         # Master agent operating guide
```

## How it works

1. Describe what you want to make
2. The agent picks a pipeline, audits available tools, proposes options with cost estimates
3. You approve, the agent generates assets (images, video clips, audio)
4. Edit in DaVinci Resolve (via MCP or manually) or compose in Remotion
5. Render the final output

## Video editing routes

Two paths to a finished video. Pick one per project, or combine them.

**Route A — DaVinci Resolve**
Full NLE. Best for: assembling AI-generated clips, color grading, audio mixing, manual creative editing. Controlled via MCP from Cursor, or hands-on in the UI. Requires Resolve installed with external scripting enabled.

**Route B — Remotion + HyperFrames + FFmpeg**
Code-based. Best for: programmatic composition, motion graphics, data-driven templates, batch rendering. No NLE needed — everything runs from the terminal.


| Task                                                      | Route                                    |
| --------------------------------------------------------- | ---------------------------------------- |
| Assemble existing clips into a timeline, grade, mix audio | **A — Resolve**                          |
| Generate motion graphics, animated titles, captions       | **B — Remotion/HyperFrames**             |
| Combine AI clips + audio into a final music video         | **A — Resolve** (or B if fully scripted) |
| Batch render templated videos with different data         | **B — Remotion**                         |
| Ambiguous                                                 | **Ask the user**                         |


## License

[GNU AGPLv3](LICENSE)

---

Forked from [OpenMontage](https://github.com/calesthio/OpenMontage) by [calesthio](https://github.com/calesthio).