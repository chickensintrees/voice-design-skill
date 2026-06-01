# The exact request — News Anchor design call

This is a **known-good, verified** Voice Design request: the precise call that produces the
news-anchor reference samples in [`samples/news-anchor/`](samples/news-anchor/). It is
generated programmatically from [`../presets/news-anchor.json`](../presets/news-anchor.json),
not transcribed by hand. Diff your own request against it field by field.

## Endpoint and headers

```
POST https://api.elevenlabs.io/v1/text-to-voice/design
xi-api-key: <YOUR_ELEVENLABS_API_KEY>
Content-Type: application/json
```

- Auth header is `xi-api-key` — **not** `Authorization: Bearer`.
- Endpoint is `/v1/text-to-voice/design` — **not** `/v1/text-to-speech` and not any
  `voice-generation` path.

## Exact request body (every field, every nested object)

```json
{
  "voice_description": "A woman in her late 40s, American, a network television news anchor. She sits at the anchor desk under warm studio lights, an earpiece in, reading from a teleprompter a few feet away but speaking as though directly to one person at home. Broadcast-trained diction — clean, warm, authoritative without strain, every consonant landing without effort. Close lavalier microphone. Treated studio room tone, almost no reverb, the very faint sense of a control room counting in her ear. Decades of live television have made her unflappable; she can move from a hard headline to a human story without a seam. Steady, grounded, fundamentally trustworthy. She speaks to camera with the easy confidence of someone who has done ten thousand broadcasts and is not nervous about the next one.",
  "model_id": "eleven_ttv_v3",
  "text": "Okay, are we good on camera two? Let me just check the prompter. Right, it's scrolling a touch fast — can we ease that back a little? And somebody grab me a water before we come back. We're back in ninety seconds, everyone.",
  "auto_generate_text": false,
  "loudness": 0.3,
  "enhance_prompt": false,
  "voice_settings": {
    "guidance_scale": 100,
    "volume_level": 0.0,
    "seed": 8160
  }
}
```

## The fields that matter most, called out

| Field | Value | Note |
|-------|-------|------|
| `model_id` | `eleven_ttv_v3` | Design model. Not `eleven_v3` (that's TTS), not `eleven_multilingual_ttv_v2`. |
| `voice_settings.guidance_scale` | `100` | **MUST be nested inside `voice_settings`.** At the top level the API silently ignores it and you get a flat, generic voice. This is the #1 cause of "bad" output. |
| `voice_settings.seed` | `8160` | Also nested in `voice_settings`. Same seed + same inputs = same voice. The portable fingerprint. |
| `voice_settings.volume_level` | `0.0` | Nested in `voice_settings`. |
| `enhance_prompt` | `false` | `true` rewrites your scene into generic ad copy. |
| `auto_generate_text` | `false` | You are supplying `text`; don't let the API invent it. |
| `loudness` | `0.3` | Top level. |
| (no `reference_audio`) | — | Omit it entirely. Reference audio fights the prompt. |

### Full `voice_description` (the scene prompt), verbatim

> A woman in her late 40s, American, a network television news anchor. She sits at the anchor desk under warm studio lights, an earpiece in, reading from a teleprompter a few feet away but speaking as though directly to one person at home. Broadcast-trained diction — clean, warm, authoritative without strain, every consonant landing without effort. Close lavalier microphone. Treated studio room tone, almost no reverb, the very faint sense of a control room counting in her ear. Decades of live television have made her unflappable; she can move from a hard headline to a human story without a seam. Steady, grounded, fundamentally trustworthy. She speaks to camera with the easy confidence of someone who has done ten thousand broadcasts and is not nervous about the next one.

### Full `text` (the mundane audition line), verbatim

> Okay, are we good on camera two? Let me just check the prompter. Right, it's scrolling a touch fast — can we ease that back a little? And somebody grab me a water before we come back. We're back in ninety seconds, everyone.

Use both of these **verbatim**. Do not paraphrase the description and do not replace the
audition text with dramatic news copy — that makes the model perform instead of talk.

## Response and saving

`/v1/text-to-voice/design` returns a `previews` array; each preview has
`generated_voice_id` and base64 audio (`audio_base_64`). Previews **expire**. To keep one
permanently (requires a free custom-voice slot on your account):

```
POST https://api.elevenlabs.io/v1/text-to-voice
{ "voice_name": "News Anchor", "generated_voice_id": "<from a preview>" }
```

## curl (copy-paste smoke test)

```bash
curl -sS -X POST https://api.elevenlabs.io/v1/text-to-voice/design \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON' | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('previews',[])), 'previews:', [p.get('generated_voice_id') for p in d.get('previews',[])])"
{
  "voice_description": "A woman in her late 40s, American, a network television news anchor. She sits at the anchor desk under warm studio lights, an earpiece in, reading from a teleprompter a few feet away but speaking as though directly to one person at home. Broadcast-trained diction — clean, warm, authoritative without strain, every consonant landing without effort. Close lavalier microphone. Treated studio room tone, almost no reverb, the very faint sense of a control room counting in her ear. Decades of live television have made her unflappable; she can move from a hard headline to a human story without a seam. Steady, grounded, fundamentally trustworthy. She speaks to camera with the easy confidence of someone who has done ten thousand broadcasts and is not nervous about the next one.",
  "model_id": "eleven_ttv_v3",
  "text": "Okay, are we good on camera two? Let me just check the prompter. Right, it's scrolling a touch fast — can we ease that back a little? And somebody grab me a water before we come back. We're back in ninety seconds, everyone.",
  "auto_generate_text": false,
  "loudness": 0.3,
  "enhance_prompt": false,
  "voice_settings": { "guidance_scale": 100, "volume_level": 0.0, "seed": 8160 }
}
JSON
```
