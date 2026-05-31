#!/usr/bin/env python3
"""Design a natural-sounding voice with ElevenLabs (eleven_ttv_v3), following the
Gold Workflow from SKILL.md:

  SCENE prompt  +  MUNDANE audition text  +  guidance_scale 100 (inside voice_settings)
  +  enhance_prompt off  +  no reference audio  +  explicit seeds.

Generates seeds x 3 previews = candidates, writes a `.mp3` + sidecars for each, and
(optionally) saves a chosen winner permanently — design previews EXPIRE.

Usage:
    export ELEVENLABS_API_KEY=sk-...

    # use a preset from ../presets (reproducible on any machine):
    python3 design_voice.py --preset ../presets/news-anchor.json

    # or run the built-in inline example:
    python3 design_voice.py

    # override seeds (default comes from the preset, or 7000/7777/4242):
    python3 design_voice.py --preset ../presets/news-anchor.json --seeds 8160

    # save a chosen preview permanently (needs a free custom-voice slot):
    python3 design_voice.py --save <generated_voice_id> "My Voice Name"

A preset is a JSON file with: voice_description, audition_text, and (optionally) seeds,
loudness, enhance_prompt, voice_settings. See ../presets/news-anchor.json.
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
API = "https://api.elevenlabs.io"

# ---------------------------------------------------------------------------
# Built-in inline example (used when no --preset is given). Edit freely.
# ---------------------------------------------------------------------------
DEFAULT = {
    "preset_name": "inline example",
    "voice_description": (
        "A woman in her late 30s, American. She is a forensic examiner who just found "
        "something unexpected in the data and is dictating her findings with controlled "
        "excitement into a desk microphone. Her voice is clear with natural resonance and "
        "energy. She speaks precisely but there is urgency underneath — she is building "
        "toward something, connecting dots in real time. Close microphone in a small "
        "office. You can hear her shift in her chair. The scratch of a pen on paper "
        "between sentences. Natural room sound. A real recording of a real person."
    ),
    "audition_text": (
        "Okay, so the third sample. Let me just pull it up. Right — same batch as the "
        "other two, logged Tuesday afternoon. Can you hand me the second folder? Thanks. "
        "And make a note that we'll need the originals back before five."
    ),
    "seeds": [7000, 7777, 4242],
    "loudness": 0.3,
    "enhance_prompt": False,
    "auto_generate_text": False,
    "voice_settings": {"guidance_scale": 100, "volume_level": 0.0},
}
# ---------------------------------------------------------------------------


def load_preset(path):
    p = json.loads(Path(path).read_text())
    # fill any missing keys from DEFAULT so partial presets still run
    merged = {**DEFAULT, **p}
    merged["voice_settings"] = {**DEFAULT["voice_settings"], **p.get("voice_settings", {})}
    return merged


def design(preset, seed):
    body = {
        "voice_description": preset["voice_description"],
        "model_id": preset.get("model_id", "eleven_ttv_v3"),
        "text": preset["audition_text"],
        "auto_generate_text": preset.get("auto_generate_text", False),
        "loudness": preset.get("loudness", 0.3),
        "enhance_prompt": preset.get("enhance_prompt", False),
        "voice_settings": {**preset["voice_settings"], "seed": seed},
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


def run_design(preset, seeds):
    slug = preset.get("preset_name", "voice").split("(")[0].strip().lower().replace(" ", "-")
    out = Path(__file__).parent / "runs" / f"{datetime.now():%Y%m%d-%H%M%S}-{slug}"
    out.mkdir(parents=True, exist_ok=True)

    params = {k: preset.get(k) for k in ("loudness", "enhance_prompt", "model_id")}
    params["voice_settings"] = preset["voice_settings"]
    manifest = {"preset": preset.get("preset_name"), "scene": preset["voice_description"],
                "text": preset["audition_text"], "params": params, "candidates": []}

    n = 0
    for seed in seeds:
        try:
            res = design(preset, seed)
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
            (out / f"{label}.prompt").write_text(preset["voice_description"])
            (out / f"{label}.text").write_text(preset["audition_text"])
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
    ap.add_argument("--preset", help="Path to a preset JSON (see ../presets/).")
    ap.add_argument("--seeds", type=int, nargs="+", help="Override the seeds to try.")
    ap.add_argument("--save", nargs=2, metavar=("GENERATED_VOICE_ID", "NAME"),
                    help="Permanently save a chosen preview's generated_voice_id.")
    args = ap.parse_args()

    if not API_KEY:
        sys.exit("Set ELEVENLABS_API_KEY in your environment first.")

    if args.save:
        gid, name = args.save
        result = save_winner(gid, name)
        print(json.dumps(result, indent=2))
        print(f"\nSaved. Permanent voice_id: {result.get('voice_id')}")
        return

    preset = load_preset(args.preset) if args.preset else DEFAULT
    seeds = args.seeds or preset.get("seeds") or [7000, 7777, 4242]
    run_design(preset, seeds)


if __name__ == "__main__":
    main()
