# Worked example: female news anchor (studio)

A complete walk-through of the Gold Workflow for one character, so you can see how
the SCENE prompt and the audition text are built. The news anchor is a useful case
because it makes the single biggest trap obvious: **do not audition her on news copy.**

> The model is an actor. Give it dramatic broadcast copy ("Breaking news tonight...")
> and it will *perform* — clipped, punchy, over-enunciated, exactly the voiceover sound
> you're trying to escape. Audition her doing something ordinary and you hear the real
> voice underneath. See "Writing for Speech" and step 2 in [`../SKILL.md`](../SKILL.md).

---

## 1. SCENE prompt (the instrument)

Put a person in a real studio. Describe the room, the mic, the training, the psychology —
not a list of adjectives.

```
A woman in her late 40s, American, a network television news anchor. She sits at
the anchor desk under warm studio lights, an earpiece in, reading from a teleprompter
a few feet away but speaking as though directly to one person at home. Broadcast-trained
diction — clean, warm, authoritative without strain, every consonant landing without
effort. Close lavalier microphone. Treated studio room tone, almost no reverb, the very
faint sense of a control room counting in her ear. Decades of live television have made
her unflappable; she can move from a hard headline to a human story without a seam.
Steady, grounded, fundamentally trustworthy. She speaks to camera with the easy
confidence of someone who has done ten thousand broadcasts and is not nervous about
the next one.
```

### Tonal variations

Change a few phrases, keep the structure. Same room, different person.

**Evening-news gravitas (serious, measured):**
```
...Her voice is lower and slower, deliberate, carrying weight. She lets small silences
sit. The authority of the last word on the day's events. Calm in a way that steadies
the room.
```

**Morning-show warmth (brighter, conversational):**
```
...Her voice is brighter and quicker, with an easy smile in it. She sounds like she's
mid-conversation with a friend over coffee, glancing at the next story, genuinely
interested. Light on her feet, warm, never slick.
```

---

## 2. MUNDANE audition text (this is what finds the voice)

She is at work, between segments, talking to the crew. Housekeeping, not headlines.

**Good (mundane — model talks like a person):**
```
Okay, are we good on camera two? Let me just check the prompter. Right, it's scrolling
a touch fast — can we ease that back a little? And somebody grab me a water before we
come back. We're back in ninety seconds, everyone.
```

**Also good (mundane, to a colleague):**
```
Did the new lead-in copy come through yet? Good, I'll read it cold. And tell the booth
I want to take the second package first, then we'll come back to the interview. You good
on time? Okay. Let's go.
```

**Bad (dramatic news copy — model ACTS, sounds like a voiceover):**
```
Breaking news tonight. A developing story out of the capital, where officials say the
situation is changing by the hour. We're live at the scene. Stay with us.
```

**Bad (a "test" sentence — tells the model nothing):**
```
Good evening. Welcome to the broadcast. Here are tonight's top stories.
```

> **Design text ≠ production text.** Audition her on the mundane crew chatter above to
> *find* the voice. Once it's saved, you generate the actual newscast — "Breaking news
> tonight..." — for real, and it will sound natural because the voice underneath is a
> real person, not a performance.

---

## 3. What fails (for contrast)

Bare traits, no scene, no room, no psychology — this gives you a generic voiceover:

```
A professional female news anchor voice. Clear, authoritative, polished. Neutral
American accent. Confident and trustworthy. Broadcast quality.
```

Every word there is true and every word is useless. The model has no room to stand in.

---

## 4. Run it

Paste the SCENE into `SCENE` and the mundane crew chatter into `TEXT` in
[`design_voice.py`](design_voice.py), then:

```bash
export ELEVENLABS_API_KEY=sk-...
python3 design_voice.py
# listen to examples/runs/<timestamp>/, pick a winner, then:
python3 design_voice.py --save <generated_voice_id> "News Anchor"
```

Settings are already the proven configuration: `eleven_ttv_v3`, `guidance_scale: 100`
inside `voice_settings`, `enhance_prompt: false`, no reference audio, explicit seeds.
