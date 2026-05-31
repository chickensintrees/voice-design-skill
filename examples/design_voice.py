#!/usr/bin/env python3
"""Design a natural-sounding voice with ElevenLabs (eleven_ttv_v3), following the
Gold Workflow from SKILL.md:

  SCENE prompt  +  MUNDANE audition text  +  guidance_scale 100 (inside voice_settings)
  +  enhance_prompt off  +  no reference audio  +  explicit seeds.

Generates N seeds x 3 previews = candidates, writes a `.mp3` + sidecars for each,
and (optionally) saves a chosen winner permanently — design previews EXPIRE.

Usage:
    export ELEVENLABS_API_KEY=sk-...
    python3 design_voice.py                 # generate candidates
    python3 design_voice.py --save <generated_voice_id> "My Voice Name"

Edit SCENE and TEXT below. That's the whole job: the prompt is the instrument.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    sys.exit("Set ELEVENLABS_API_KEY in your environment first.")

API = "https://api.elevenlabs.io"

# ---------------------------------------------------------------------------
# EDIT THESE TWO. Everything else is the proven configuration.
# ---------------------------------------------------------------------------

# SCENE — a person in a room doing something specific, not a list of adjectives.
SCENE = (
    "A woman in her late 30s, American. She is a forensic examiner who just found "
    "something unexpected in the data and is dictating her findings with controlled "
    "excitement into a desk microphone. Her voice is clear with natural resonance and "
    "energy. She speaks precisely but there is urgency underneath — she is building "
    "toward something, connecting dots in real time. Her pacing is deliberate with "
    "purposeful pauses where she is thinking. Close microphone in a small office. You "
    "can hear her shift in her chair. The scratch of a pen on paper between sentences. "
    "Natural room sound. A real recording of a real person, genuinely engaged."
)

# MUNDANE audition text — housekeeping, not the dramatic monologue. Lets the real
# voice show. Dialogue, not exposition. No fake "uh"/"um" disfluency.
TEXT = (
    "Okay, so the third sample. Let me just pull it up. Right — same batch as the "
    "other two, logged Tuesday afternoon. Can you hand me the second folder? Thanks. "
    "And make a note that we'll need the originals back before five."
)

SEEDS = [7000, 7777, 4242]  # explicit, reproducible. Add more for a wider audition.

# ---------------------------------------------------------------------------


def design(seed):
    body = {
        "voice_description": SCENE,
        "model_id": "eleven_ttv_v3",
        "text": TEXT,
        "auto_generate_text": False,
        "loudness": 0.3,
        "enhance_prompt": False,
        "voice_settings": {"guidance_scale": 100, "volume_level": 0.0, "seed": seed},
    }
    req = urllib.request.Request(
        f"{API}/v1/text-to-voice/design",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def save_winner(generated_voice_id, name):
    """Design previews expire. This makes the voice permanent. Returns the voice_id."""
    body = {"voice_name": name, "generated_voice_id": generated_voice_id}
    req = urllib.request.Request(
        f"{API}/v1/text-to-voice",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def run_design():
    out = Path(__file__).parent / "runs" / f"{datetime.now():%Y%m%d-%H%M%S}"
    out.mkdir(parents=True, exist_ok=True)

    params = {"guidance_scale": 100, "enhance_prompt": False, "loudness": 0.3,
              "model_id": "eleven_ttv_v3", "reference_audio": None}
    manifest = {"scene": SCENE, "text": TEXT, "params": params, "candidates": []}

    n = 0
    for seed in SEEDS:
        try:
            res = design(seed)
        except urllib.error.HTTPError as e:
            print(f"seed {seed}: HTTP {e.code} {e.read().decode()[:300]}")
            continue
        for i, p in enumerate(res.get("previews", [])):
            n += 1
            label = f"cand-{n:02d}-seed{seed}-{i + 1}"
            b64 = p.get("audio_base_64") or p.get("audio_base64")
            if not b64:
                print(f"{label}: no audio in preview; keys={list(p.keys())}")
                continue
            (out / f"{label}.mp3").write_bytes(base64.b64decode(b64))
            gid = p.get("generated_voice_id") or ""
            # Sidecars: the backup if the preview expires before you save it.
            (out / f"{label}.voice_id").write_text(gid)
            (out / f"{label}.seed").write_text(str(seed))
            (out / f"{label}.prompt").write_text(SCENE)
            (out / f"{label}.text").write_text(TEXT)
            (out / f"{label}.params").write_text(json.dumps({**params, "seed": seed}, indent=2))
            manifest["candidates"].append(
                {"label": label, "seed": seed, "generated_voice_id": gid,
                 "duration_secs": p.get("duration_secs"), "file": f"{label}.mp3"})
            print(f"  {label}.mp3  (generated_voice_id={gid})")

    (out / "_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n{n} candidates -> {out}")
    print("Listen, pick a winner, then save it (previews expire):")
    print(f"  python3 {Path(__file__).name} --save <generated_voice_id> \"My Voice Name\"")


def main():
    ap = argparse.ArgumentParser(description="ElevenLabs voice design (Gold Workflow).")
    ap.add_argument("--save", nargs=2, metavar=("GENERATED_VOICE_ID", "NAME"),
                    help="Permanently save a chosen preview's generated_voice_id.")
    args = ap.parse_args()

    if args.save:
        gid, name = args.save
        result = save_winner(gid, name)
        print(json.dumps(result, indent=2))
        print(f"\nSaved. Permanent voice_id: {result.get('voice_id')}")
    else:
        run_design()


if __name__ == "__main__":
    main()
