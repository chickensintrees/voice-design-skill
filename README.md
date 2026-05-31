# voice-design

A portable skill for designing **natural-sounding voices** with the ElevenLabs Voice Design + Text-to-Speech APIs.

Most AI voice output sounds like a voiceover. This skill is the accumulated method for making it sound like a *person* — built from 50+ voice candidates, 7 failed approaches, and one voice good enough to forensically recover after it was lost.

The one-line version: **the prompt is the instrument.** You don't pick a voice from sliders. You write a scene, put a person in a room, and record them.

## What's here

- **[`SKILL.md`](SKILL.md)** — the skill itself. The Gold Workflow, the parameter rules, the words that kill voices and the words that give them life. This is the thing you install.
- **[`examples/design_voice.py`](examples/design_voice.py)** — a self-contained, dependency-free reference implementation. Generates candidates, writes reproducibility sidecars, and saves a winner. Edit two strings and run it.
- **[`examples/news-anchor.md`](examples/news-anchor.md)** — a fully worked SCENE + audition-text example (female news anchor, studio), including tonal variations and the trap to avoid.
- **[`presets/`](presets/)** — ready-to-run voice presets as JSON, each with a proven seed. Reproducible on any machine: `python3 examples/design_voice.py --preset presets/<name>.json`.

## Quick start (the script)

```bash
export ELEVENLABS_API_KEY=sk-...      # your ElevenLabs key
python3 examples/design_voice.py      # generate candidates into examples/runs/

# listen, pick the one you like, then make it permanent (previews expire):
python3 examples/design_voice.py --save <generated_voice_id> "My Voice Name"
```

No pip install required — standard library only.

## Installing the skill

### Claude Code (CLI)

Drop the skill into your skills directory:

```bash
mkdir -p ~/.claude/skills/voice-design
curl -o ~/.claude/skills/voice-design/SKILL.md \
  https://raw.githubusercontent.com/<your-user>/voice-design-skill/main/SKILL.md
```

(Or for a single project: `.claude/skills/voice-design/SKILL.md` inside the repo.)
It registers automatically. Invoke it with `/voice-design` or just ask Claude to design a voice.

### Claude (web / Coworker)

Add `SKILL.md` as a **Skill** (or attach it as project knowledge / a custom instruction file). The content is plain Markdown — paste it into a project's knowledge or upload the file, and reference it when you want a voice designed.

### Cursor

Save the skill as a project rule so the agent always has it:

```bash
mkdir -p .cursor/rules
# save SKILL.md's body as a rule (Cursor reads .mdc / .md rules from .cursor/rules)
cp SKILL.md .cursor/rules/voice-design.md
```

Then ask Cursor's agent to design a voice; it will pull the rule into context.

## Presets

Each file in [`presets/`](presets/) is a complete, tested recipe — scene prompt, mundane
audition text, the proven seed, and the standard settings. Run one directly:

```bash
python3 examples/design_voice.py --preset presets/news-anchor.json
# pin to the proven seed for the known-good voice:
python3 examples/design_voice.py --preset presets/news-anchor.json --seeds 8160
```

| Preset | Voice | Proven seed |
|--------|-------|-------------|
| [`news-anchor.json`](presets/news-anchor.json) | Female network news anchor, studio | `8160` |

A preset stores everything needed to reproduce the voice **except** the
`generated_voice_id` — that changes per call and is tied to your ElevenLabs account, so
the portable fingerprint is the seed. Drop a new JSON in `presets/` to add your own.

## The short version of the method

1. Write a **SCENE** prompt — a person in a room, mic placement, room tone, psychology, stakes. Not adjectives.
2. Write **MUNDANE** audition text — the character doing ordinary work, not their dramatic monologue. This is what makes the model talk instead of act.
3. `model_id: eleven_ttv_v3`, `guidance_scale: 100` **inside `voice_settings`**, `enhance_prompt: false`, no reference audio, explicit seed.
4. Generate several seeds, audition, **save the winner immediately** (design previews expire), and write sidecars (`.voice_id`, `.seed`, `.prompt`, `.text`, `.params`).

Read [`SKILL.md`](SKILL.md) for the full reasoning behind every one of those.

## License

MIT — see [LICENSE](LICENSE).

Not affiliated with ElevenLabs. "ElevenLabs" is a trademark of its owner. Model IDs and API behavior are current as of early 2026 and may change.
