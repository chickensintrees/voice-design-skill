---
name: voice-design
description: ElevenLabs voice design and TTS mastery. Accumulated lessons from 50+ voice candidates, 7 failed approaches, and 1 forensic voice recovery. Teaches scene-based prompting, the Gold Workflow, and why the prompt is the instrument.
user-invocable: true
---

# Voice Design

You are designing a voice. Not picking a preset. Not tweaking sliders. Building a person who happens to be speaking.

This skill contains everything learned from 50+ voice candidates, 7 failed approaches, and one voice so good it was lost and recovered through two days of forensic work to understand why it worked.

The lesson that took the longest to learn: **the prompt is the instrument.** Not the reference audio. Not the tags. Not the settings. The words you use to describe the scene.

## The Model Rule

**ALWAYS use `eleven_ttv_v3` for voice design and `eleven_v3` for TTS.** Not `multilingual_v2`. Not `multilingual_ttv_v2`. Those are older. The v3 models support reference audio, higher guidance scale adherence, and audio tags. If you catch yourself using any other model ID, stop and switch.

## The Gold Workflow

This is the proven sequence. Every step matters. Skipping one costs you a voice.

### 1. Write a SCENE Prompt (max 1000 chars)

This is the instrument. The model doesn't make a voice from adjectives. It places a person in a room and records them.

**What works (SCENE):**
```
"A British man in his mid 60s. Upper class but understated — old money
worn thin. He is sitting behind a desk in a quiet room, speaking directly
to someone across from him. Close microphone. The room is still. His voice
is soft but carries absolute authority. Every word is measured, deliberate.
He has delivered interrogations that felt like conversations. Quiet, never
dramatic. Soft power. Slightly weary from decades of seeing through lies.
A retired intelligence officer making one more offer. Natural room sound.
Chair creak. Pen tap on wood."
```

**What fails (TRAITS):**
```
"A British male voice in his forties. Measured, precise, controlled. RP
accent with Whitehall authority. Each word placed with care. Cold,
professional."
```

The first one creates a person in a room. The second creates a voiceover.

### 2. Write MUNDANE Preview Text (100-1000 chars)

**THE TEXT DETERMINES WHETHER THE MODEL ACTS OR TALKS.** This is the single most important lesson from 60+ candidates across 3 characters. Dramatic/existential text makes the model perform dramatically. Mundane conversational text makes it talk like a person.

The preview text for voice DESIGN should be the character doing ordinary things. Not their big moment. Not their emotional scene. Just a person at work, talking to someone about normal business.

**Good (mundane — model talks naturally):**
```
"The Patterson brief should have been on my desk this morning. Has Richards
called back about the lease? Good. And push the board meeting to three,
would you? I want to read through the quarterly before I go in there."
```

**Good (mundane — model talks naturally):**
```
"Oh, the Hargrove file? Second cabinet, third drawer. I already pulled it
this morning. And your coffee is on your desk, two sugars, no cream. The
Patterson meeting got moved to Thursday so you've got the whole morning."
```

**Bad (dramatic — model ACTS):**
```
"Someone needs to be here. To witness it. To document the stories.
To remember everything. Even the things that hurt."
```

**Bad (test sentence):**
```
"The quick brown fox jumps over the lazy dog. This is a sample of how
the voice will sound in various contexts."
```

The dramatic text produces voices that sound like actors reading stage directions. The mundane text produces voices that sound like people. This was proven across 4 rounds of iteration — same scene prompt, same settings, different text. The text was the variable that mattered.

**Voice design text ≠ production VO text.** The design preview is for finding the voice. The production lines can be dramatic, emotional, whatever the script needs. But the audition text must be mundane or you'll never hear the real voice underneath the performance.

**No fake disfluency in design text.** Don't sprinkle "uh," "to... to," or "I... I don't know" into prose. The model reads these as stage directions for hesitation and sounds like a bad actor. Real speech pauses at thought boundaries, not mid-word. Let the model breathe naturally.

### 3. Set Parameters

```json
{
  "voice_description": "YOUR SCENE PROMPT",
  "model_id": "eleven_ttv_v3",
  "text": "YOUR MUNDANE DIALOGUE",
  "auto_generate_text": false,
  "loudness": 0.3,
  "enhance_prompt": false,
  "voice_settings": {
    "guidance_scale": 100,
    "volume_level": 0.0,
    "seed": GENERATE_ONE
  }
}
```

**CRITICAL:** `guidance_scale` goes INSIDE `voice_settings`. At top level it is silently ignored. This cost three rounds of bad voices before it was found.

### 4. Generate an Explicit Seed

Never allow random seeds. Generate your own. Store it in a `.seed` sidecar next to the audio file. Same seed + same inputs = same voice. A good voice without its seed is a key without a lock.

### 5. Call the Design Endpoint

`POST /v1/text-to-voice/design` — returns 3 previews per call.

Run 3-6 configs (different seeds) = 9-18 candidates. This gives enough range for a real audition.

### 6. Pick a Winner → SAVE IMMEDIATELY

Voice design previews are **temporary**. They expire. The best voice in this whole record was lost this way.

```
POST /v1/text-to-voice
{ "generated_voice_id": "from-the-preview" }
```

### 7. Write ALL Sidecars

Next to the audio file:
- `.voice_id` — the generated_voice_id
- `.prompt` — the exact voice_description text
- `.text` — the exact preview text
- `.seed` — the seed value
- `.params` — JSON of all parameters

These are your backup. If the voice expires, the sidecars let you get close again.

### 8. Reference Audio Is Actively Harmful

Tested across 3 characters. **All three won WITHOUT reference audio.** In one case, adding a stock voice reference made the output noticeably worse — a weird hybrid that sounded artificial.

The prompt is the instrument. Reference audio fights with the prompt instead of helping it. Don't use it unless you have a very specific reason and are prepared for it to make things worse.

## Seven Things That Give Voices Life

1. **SCENE not traits.** "Sitting behind a desk, speaking directly to someone across from him." The performance comes from the situation.
2. **Mic placement.** "Close microphone." Three words. Makes the recording intimate.
3. **Acoustic environment.** "Natural room sound. Chair creak. Pen tap on wood." This is what makes it sound real.
4. **Character psychology.** "Delivered interrogations that felt like conversations." Not just how they sound. Who they are.
5. **Specific behavioral history.** "Slightly weary from decades of seeing through lies." Backstory shapes delivery.
6. **Stakes and motivation.** "Making one more offer." Implies narrative. The model performs differently when the character wants something.
7. **Preview text as performance.** "Sit down. There is tea, if you want it." Give the model a scene to inhabit, not a sentence to read.

## Words That Kill Voices

- "tired," "flat affect," "breathiness," "trailing" — makes voice sound BORED
- "warm," "soothing," "gentle" — meditation app voice
- Any exhaustion markers pull toward monotone

## Words That Give Life

- "alert," "sharp," "focused," "engaged"
- "controlled excitement," "building toward something," "connecting dots"
- "urgency underneath," "slight edge," "detective energy"
- "occasionally surprised by what she is finding"
- "speaking directly to someone" — conversational, not performative

## TTS Settings

```json
{
  "model_id": "eleven_v3",
  "voice_settings": {
    "stability": 0.0,
    "similarity_boost": 0.5
  }
}
```

- **stability 0.0** = Creative. Max expressiveness. Audio tags most responsive.
- **stability 0.5** = Natural. Middle ground.
- **stability 1.0** = Robust. Dampens audio tags and expressiveness.
- v3 stability is discrete: 0.0, 0.5, or 1.0. Other values cause 400 errors.

## Audio Tags (v3 TTS)

Square brackets in TTS text affect delivery:
- `[sighs]`, `[whispers]`, `[laughs]`, `[curious]`, `[sarcastic]`
- `[strong French accent]` — accent control
- Works best with Creative stability (0.0)
- Experimental: sometimes read aloud instead of performed
- Start sections with a tag (like `[clears throat]`) to prime the model

## Text Formatting for Performance

- **Ellipses (...)** — create pauses, emphasize weight
- **CAPS** — increase emphasis: "a VERY long day"
- **Dashes (— or --)** — hesitation: "Wait — what's that noise?"
- SSML `<break>` works in v2 only, NOT v3

## Writing for Speech (NOT Writing Prose)

TTS scripts must read like raw dictation. Real people say "uh" and "um." They repeat words. They false-start. They trail off and restart. They use "right?" rhetorically. They stumble on numbers.

If a TTS script reads cleanly, it will SOUND like a voiceover. Messiness = humanity.

The deeper lesson: you can't fake humanity by sprinkling filler words on complete sentences. Start from nothing. Become the person. What are they looking at? What surprises them? Where do they lose their place?

## The Learning Record

Seven approaches that failed before the pattern emerged (a narrative trailer project):

1. Stock premade voices → "sound like voiceovers"
2. Premade at stability 0.0 → still voiceovers
3. Voice Design with "flat affect," "tired" → "too bored"
4. Removed "tired," added "engaged" → still bored (guidance_scale at wrong level)
5. Full acoustic scene, "alert and focused" → "sounds real now, but bored"
6. guidance_scale INSIDE voice_settings + detective energy → **"works"**
7. Winning prompt rewritten "richer" for redesign → worse than original

Four more rounds that refined the pattern (a second project, character A):

8. guidance 20, enhance ON, dramatic text with fake disfluency → "bad actors reading lines"
9. guidance 20, enhance OFF, no ref, dramatic text without disfluency → "falling asleep"
10. guidance 100, no enhance, no ref, dramatic/existential text → still acting, not talking
11. guidance 100, no enhance, no ref, **mundane conversational text** → **"that's the one"**

Round 11 was the breakthrough. Same scene prompt as round 10. Same settings. Only the TEXT changed — from "Someone needs to be here. To witness it." to "Oh, the Hargrove file? Second cabinet, third drawer." The text was the only variable. It changed everything.

A third character confirmed the pattern in one round. Same settings as character A's round 11. First try. 12 candidates, winner picked immediately.

**The winning configuration (proven across 3 characters):**

| Parameter | Value | Why |
|-----------|-------|-----|
| guidance_scale | 100 | Inside voice_settings. Higher = more adherence to prompt |
| enhance_prompt | false | AI rewriting fights the scene prompt |
| reference_audio | none | Tested 3 times. No-ref won every time |
| preview text | mundane | Normal text = natural voice. Dramatic = acting |
| fake disfluency | none | "uh" in prose = stage directions for hesitation |

The hardest lesson: When you have a prompt that works, **use it verbatim.** Don't improve it. Don't rewrite it richer. The magic is in the specific word choices. The prompt is the instrument. Don't retune it.

## Where This Came From

60+ voice candidates across 3 characters. Two lost voices (one forensically recovered). Eleven failed approaches. Reference audio tested 3 times, lost 3 times. The preview-text breakthrough came from 4 rounds on one character — same prompt, same settings, only the text changed.

The damage from losing a voice without its seed taught the sidecar system. The damage from rewriting a winning prompt taught us to leave it alone. The damage from dramatic preview text taught us that the model is an actor — give it a mundane scene and it relaxes into being a person. Every rule here cost something.
