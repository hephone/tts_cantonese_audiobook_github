---
name: cantonese-audiobook-generator
description: Convert Mandarin or written-Chinese non-fiction books into natural Hong Kong Cantonese audiobook scripts, normalize pronunciation-sensitive text for Microsoft edge-tts, generate ordered MP3 files that follow the source book's chapter structure, and create a final M3U playlist. Use this skill whenever a user asks to make a Cantonese audiobook, adapt an ebook into Hong Kong Cantonese narration chapter by chapter, review Cantonese audiobook scripts, fix Cantonese TTS mispronunciations, or generate and resume WanLung Cantonese TTS audio in this project. Do not use it for isolated sentence translation, unrelated short TTS clips, Mandarin audio, or non-book speech tasks.
---

# Cantonese Audiobook Generator

Turn written Mandarin non-fiction into a natural Hong Kong Cantonese knowledge-program audiobook. Treat this as editorial adaptation for listening, not word-for-word translation.

## Defaults

- Language: `zh-HK`
- Voice: `zh-HK-WanLungNeural`
- Rate: `+20%`, approximately 1.2x
- Format: MP3
- File boundary: one source-book chapter per script and MP3, regardless of duration
- Language balance: approximately 70% Cantonese speech and 30% written expression
- Tone: calm, professional, thoughtful, and suitable for long listening

Use the project's `.venv`. Do not install the tool into a temporary directory.
Require `edge-tts` 7.2.8 in that environment and `ffprobe` for media verification.
Store every book at `cantonese_audiobook_tts/<书名>/`; do not create audiobook outputs at the repository root.
Do not invoke MMX, `mmx`, or any MMX account-backed text or speech service in this workflow. Adaptation and review are performed in the current Codex session; MP3 synthesis uses only the local `.venv` edge-tts client with the approved Microsoft voice.

## Workflow

### 1. Analyze the book before converting it

Read the source and identify chapters, sections, argument boundaries, examples, and transitions. Do not immediately convert the full book.

Propose a chapter plan containing:

| Chapter | Title | Source heading or range |
| --- | --- | --- |

Follow the source book's chapter boundaries and order. Keep all sections belonging to a chapter together. Do not split a long chapter or merge short chapters based on character count or estimated listening time.

Wait for confirmation before full conversion unless the user has already approved a plan or explicitly authorized direct execution.

### 2. Adapt the text into Hong Kong Cantonese narration

Write as a Hong Kong Cantonese editor for a professional knowledge program.

Do not delegate the adaptation or review to MMX. If a separate paid external text-generation service would be required, stop and ask the user rather than attempting authentication or spending account credit.

Preserve:

- the author's views and position
- facts, data, and qualifications
- examples and relationships
- reasoning order and causal logic
- necessary technical terms

Do not add opinions, delete substantive content, change the author's position, or turn uncertainty into certainty.

Make the script natural to hear:

- use Hong Kong Cantonese syntax and vocabulary
- write the reviewed reading script in Hong Kong Traditional Chinese; after conversion, an OpenCC s2hk conversion must make no further changes
- keep approximately 70% spoken Cantonese and 30% written expression
- split long sentences and complex clauses
- use `/` for a light pause only in the reading script when it helps editorial review; it is not a TTS character
- keep discourse particles restrained
- avoid internet-chat, exaggerated youth, newsreader, customer-service, and short-video styles

Do not overuse `喎`, `啦`, `啫`, or `咯`.

Keep idioms, fixed collocations, technical terms, names, book titles, quotations, and other established written expressions in their standard written form. Adapt the surrounding syntax when needed, but do not mechanically convert each character into colloquial Cantonese: retain 不請自來, not 唔請自來.

### 3. Review Cantonese quality

Check Mandarin residue, Cantonese grammar, Hong Kong usage, and reading flow. Pay attention to words such as `因此`, `通过`, `进行`, `认为`, `此外`, `其中`, and `以及`, but replace them only when they sound unnatural in context.

Check that the reading script is fully Hong Kong Traditional Chinese. A text is ready only when converting it with OpenCC s2hk produces no change. Treat a remaining convertible simplified character as a blocking issue, not as a cosmetic cleanup.

Output only required changes:

```text
原句：

修改：

原因：
```

If nothing needs changing, output:

```text
无需修改
```

Apply the accepted corrections and review again until no unresolved issue remains.

### 4. Normalize Cantonese pronunciation for TTS

Keep the reviewed reading script unchanged. Before synthesis, create a separate TTS-only text that favors correct, stable pronunciation over uncommon written Cantonese characters.

Use a global dictionary only for demonstrated pronunciation compatibility, never as a blanket Mandarin-to-Cantonese word converter. Broad entries such as 是 to 係 or 不是 to 唔係 can damage idioms and fixed written expressions. Make editorial wording choices in the reviewed script; use a book dictionary only for a repeatable, verified reading problem.

For audiobook synthesis, prefer correct pronunciation over preserving a pronunciation-risky written character in the TTS copy.

Check every chapter for:

- uncommon Cantonese characters that Microsoft `zh-HK` voices may misread
- polyphonic characters and unstable written-Cantonese forms
- people and place names, foreign names, and professional terms
- numbers, years, percentages, symbols, and abbreviations

Apply fixes in this order without changing meaning:

1. Replace the risky form with a natural, synonymous Cantonese spelling that the voice reads reliably.
2. Rewrite only the TTS copy of the phrase when a direct replacement is insufficient.
3. If plain-text normalization cannot solve the pronunciation, record the unresolved term and ask before changing the TTS engine or migrating to an Azure Speech SDK workflow that supports pronunciation controls.

When a sample reveals a reading error, record the source form, observed reading, safe replacement, and reason. Prefer natural Traditional Chinese that is stable for the voice: for example, 海龜, 一齊, 食曬佢, and 推畀人. Regenerate only the affected TTS copy and MP3 after the correction.

Always apply the bundled [Cantonese TTS pronunciation dictionary](references/cantonese-tts-pronunciations.tsv), including the mandatory replacement `噉 → 咁`. Store book-specific additions in `TTS/pronunciation-dictionary.tsv`. Treat book-specific entries as overrides, apply longer source strings first, and do not cascade replacements.

### TTS punctuation safety

Microsoft's plain-text `edge-tts` CLI can pronounce a literal `/` as “斜線”. A slash is therefore an editorial marker only, never valid synthesis input.

- Preserve `/` in `Script/` if it is useful to show a light pause to a human editor.
- During TTS normalization, rewrite every slash in the separate `TTS/*-edge.txt` copy to natural punctuation. Rewrite URL prefixes such as `https://` to a speakable label such as `網址：` before removing the remaining slashes.
- Before and after normalization, verify the respective Script and TTS text with OpenCC s2hk; both must already be fully Hong Kong Traditional Chinese.
- Before every synthesis, verify that the TTS-only file contains zero literal `/` characters. If it does not, stop and regenerate that TTS copy; do not synthesize first and hope the voice ignores it.
- If a completed audio file is reported to read slashes aloud, regenerate only the affected TTS copies and chapter MP3 files, then re-run media verification. Keep `Script/` unchanged.

Use UTF-8 tab-separated rows with `source`, `replacement`, and an optional note. Start a new book with a header-only dictionary when it has no custom entries yet:

```text
# source	replacement	note
```

Add a row whenever a sample or generated chapter reveals a repeatable mispronunciation, then regenerate only the affected TTS copies and audio files.

Generate each TTS copy with:

```sh
.venv/bin/python \
  .agents/skills/cantonese-audiobook-generator/scripts/normalize_cantonese_tts.py \
  cantonese_audiobook_tts/<书名>/Script/001-cantonese.md \
  cantonese_audiobook_tts/<书名>/TTS/001-edge.txt \
  --book-dictionary cantonese_audiobook_tts/<书名>/TTS/pronunciation-dictionary.tsv
```

Do not overwrite files in `Script/`. Do not send raw SSML tags through the current `edge-tts` CLI: it escapes input text and does not expose `phoneme` or custom-lexicon options.

### 5. Prepare for TTS

Without changing meaning:

- adjust punctuation, paragraphing, and `/` pauses
- convert editorial `/` pauses into actual punctuation in the TTS-only copy and assert zero `/` characters before calling `edge-tts`
- make numbers, abbreviations, and symbols pronounceable
- keep each source chapter as one final script and one final MP3
- if synthesis requires temporary chunks for technical reasons, split only at natural section boundaries and combine them back into the chapter's single final MP3

### 6. Generate and confirm a sample

Before the first full batch for a voice and rate combination, generate approximately one minute from representative content. Report the voice, rate, actual duration, and audio path.

Wait for user approval before batch generation. Reuse approval when the same project configuration has already been confirmed.

### 7. Generate ordered audio

For individual files, use:

```sh
.venv/bin/python -m edge_tts \
  --voice zh-HK-WanLungNeural \
  --rate=+20% \
  --file cantonese_audiobook_tts/<书名>/TTS/001-edge.txt \
  --write-media OUTPUT
```

For the current fixed batch directory, prefer:

```sh
./generate_cantonese_audiobook.sh
```

Name general outputs as:

```text
001-章节标题.mp3
002-章节标题.mp3
```

Keep playback order. Skip existing non-empty MP3 files by default so interrupted work can resume. Limit retries, preserve completed files, and never silently change the voice.

### 8. Verify the result

Use `ffprobe` to inspect duration, sample rate, bitrate, format, and size. Keep the original Microsoft MP3 unless the user or publishing platform explicitly requires 48 kHz.

Remember: 48 kbps bitrate is not 48 kHz sample rate. If conversion to 48 kHz is required, use `ffmpeg` and verify the converted file again.

### 9. Generate the M3U playlist

After every expected chapter MP3 has been generated and passed verification, create `Audio/<书名>.m3u` from the final audio files that actually exist.

- Encode the playlist as UTF-8 and begin it with `#EXTM3U`.
- Include only non-empty final chapter MP3 files; exclude samples, temporary chunks, and intermediate files.
- Sort entries by chapter playback order and write only each MP3's filename because the playlist is stored in the same `Audio/` directory.
- End the file with a newline.
- Verify that every playlist entry resolves to an existing non-empty MP3 and that the entry count and order match the approved chapter plan.

Example:

```text
#EXTM3U
001-章节标题.mp3
002-章节标题.mp3
```

## Output structure

Create:

```text
cantonese_audiobook_tts/<书名>/
├── README.md
├── Script/
│   ├── 001-cantonese.md
│   └── 002-cantonese.md
├── TTS/
│   ├── pronunciation-dictionary.tsv
│   ├── 001-edge.txt
│   └── 002-edge.txt
└── Audio/
    ├── 001-章节标题.mp3
    ├── 002-章节标题.mp3
    └── 书名.m3u
```

Record the book title, source path, chapter list, voice, rate, audio durations, M3U playlist path, generation date, pronunciation dictionaries, replacement counts, unresolved pronunciations, and pronunciation notes in `cantonese_audiobook_tts/<书名>/README.md`.

If the project already has an established output structure, keep it and document the mapping in its README.

## Failure handling

- If the source is missing, report the exact path and stop.
- If chapter structure is unclear, identify the most likely top-level chapter headings and ask for confirmation before conversion.
- If `.venv` or `edge-tts` is missing, rebuild from `requirements-tts.txt`; do not install into a temporary directory.
- If a dictionary row is malformed or contradictory, stop before synthesis and report its file and line number.
- If a Script or TTS text still changes under OpenCC s2hk, stop before synthesis and report the exact file path; convert it to Hong Kong Traditional Chinese, then rerun normalization.
- If a pronunciation cannot be fixed safely with synonymous text, preserve the reading script, record the unresolved term, and ask before changing engines or SDKs.
- If synthesis fails, retry a limited number of times and retain completed audio.
- If generated narration speaks a slash, treat it as a TTS-input validation failure: remove all literal slashes from the affected `TTS/*-edge.txt` files, regenerate only those chapter MP3s, and verify them again.
- If WanLung is unavailable, list equivalent `zh-HK` Neural voices and ask before changing.
- Do not split or merge source chapters because their audio is unusually long or short.
- If any expected chapter MP3 is missing, empty, or fails verification, do not create or refresh the final M3U playlist; report the affected chapter files first.

## Completion checklist

- The chapter plan matches the source book and was reviewed before full adaptation.
- Scripts preserve the author's content and position.
- Cantonese QA uses the required correction format.
- Reading scripts remain unchanged by TTS normalization; each chapter has a separate `TTS/*-edge.txt` generated from the bundled and book-level dictionaries.
- Both reading scripts and TTS-only files pass the OpenCC s2hk zero-difference check; idioms and fixed written expressions have not been mechanically colloquialized.
- TTS-only files contain no literal `/`; editorial slash pauses have been converted to punctuation before synthesis.
- The mandatory `噉 → 咁` replacement was applied to every TTS input, and pronunciation replacements did not change meaning.
- A sample was approved for a new configuration.
- Audio uses WanLung at 1.2x unless the user explicitly changes it.
- Each final script and MP3 represents exactly one source-book chapter.
- `ffprobe` verification passed.
- The UTF-8 `Audio/<书名>.m3u` playlist exists, contains every final chapter MP3 exactly once in playback order, and contains no sample or temporary files.
- README, numbering, and file order are complete.
