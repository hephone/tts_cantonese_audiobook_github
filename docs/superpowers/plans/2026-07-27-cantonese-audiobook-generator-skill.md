# Cantonese Audiobook Generator Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a project-level Codex skill that turns Mandarin non-fiction books into structured Hong Kong Cantonese audiobook scripts and generates resumable MP3 output with the project's existing Microsoft edge-tts environment.

**Architecture:** Store the workflow in one project-local `SKILL.md` so Codex can trigger it from task intent. Reuse the existing `.venv`, `edge-tts`, and batch generator rather than bundling duplicate TTS code. Store three lightweight evaluation prompts beside the skill to verify planning, Cantonese adaptation, and confirmed-generation behavior.

**Tech Stack:** Codex project skills, Markdown, JSON, Python 3.12, edge-tts 7.2.8, ffprobe

## Global Constraints

- Install the skill at `.agents/skills/cantonese-audiobook-generator/`.
- Use `.venv/bin/python` and the already installed `edge-tts==7.2.8`; do not install dependencies into a temporary directory.
- Use `zh-HK-WanLungNeural` at `+20%`, approximately 1.2x, by default.
- Target 20–40 minutes per episode, with approximately 30 minutes preferred.
- Use approximately 70% Cantonese speech and 30% written expression.
- Preserve the author's views, data, examples, logic, and position.
- Generate an approximately one-minute sample before the first full batch for a configuration.
- Use MP3 output and verify actual media properties with `ffprobe`.
- Do not treat 48 kbps bitrate as 48 kHz sample rate.
- Do not expose credentials, tokens, cookies, or secrets.
- The current workspace is not a Git repository, so do not run commit steps.

---

### Task 1: Create the Project Skill

**Files:**
- Create: `.agents/skills/cantonese-audiobook-generator/SKILL.md`

**Interfaces:**
- Consumes: Project source books, `.venv/bin/edge-tts`, `cantonese_audiobook_tts/generate_all.py`, and `generate_cantonese_audiobook.sh`
- Produces: A discoverable Codex skill named `cantonese-audiobook-generator`

- [ ] **Step 1: Verify the skill does not already exist**

Run:

```sh
test ! -e .agents/skills/cantonese-audiobook-generator/SKILL.md
```

Expected: exit status 0.

- [ ] **Step 2: Create `SKILL.md` with the approved workflow**

Create the file with this content:

```markdown
---
name: cantonese-audiobook-generator
description: Convert Mandarin or written-Chinese non-fiction books into natural Hong Kong Cantonese audiobook scripts and generate ordered MP3 chapters with the project's Microsoft edge-tts setup. Use this skill whenever a user asks to make a Cantonese audiobook, adapt an ebook into Hong Kong Cantonese narration, plan 20–40 minute listening episodes, review Cantonese audiobook scripts, or generate and resume WanLung Cantonese TTS audio in this project. Do not use it for isolated sentence translation, unrelated short TTS clips, Mandarin audio, or non-book speech tasks.
compatibility: Requires the project Python environment at .venv, edge-tts 7.2.8, and ffprobe for media verification.
---

# Cantonese Audiobook Generator

Turn written Mandarin non-fiction into a natural Hong Kong Cantonese knowledge-program audiobook. Treat this as editorial adaptation for listening, not word-for-word translation.

## Defaults

- Language: `zh-HK`
- Voice: `zh-HK-WanLungNeural`
- Rate: `+20%`, approximately 1.2x
- Format: MP3
- Episode length: 20–40 minutes; prefer approximately 30 minutes
- Language balance: approximately 70% Cantonese speech and 30% written expression
- Tone: calm, professional, thoughtful, and suitable for long listening

Use the project's `.venv`. Do not install the tool into a temporary directory.

## Workflow

### 1. Analyze the book before converting it

Read the source and identify chapters, sections, argument boundaries, examples, and transitions. Do not immediately convert the full book.

Propose an episode plan containing:

| Episode | Title | Content range | Estimated duration |
| --- | --- | --- | --- |

Place boundaries at complete arguments, cases, or sections. Do not cut mechanically by character count. Target 20–40 minutes per file.

Wait for confirmation before full conversion unless the user has already approved a plan or explicitly authorized direct execution.

### 2. Adapt the text into Hong Kong Cantonese narration

Write as a Hong Kong Cantonese editor for a professional knowledge program.

Preserve:

- the author's views and position
- facts, data, and qualifications
- examples and relationships
- reasoning order and causal logic
- necessary technical terms

Do not add opinions, delete substantive content, change the author's position, or turn uncertainty into certainty.

Make the script natural to hear:

- use Hong Kong Cantonese syntax and vocabulary
- keep approximately 70% spoken Cantonese and 30% written expression
- split long sentences and complex clauses
- use `/` for a light pause
- keep discourse particles restrained
- avoid internet-chat, exaggerated youth, newsreader, customer-service, and short-video styles

Do not overuse `喎`, `啦`, `啫`, or `咯`.

### 3. Review Cantonese quality

Check Mandarin residue, Cantonese grammar, Hong Kong usage, and reading flow. Pay attention to words such as `因此`, `通过`, `进行`, `认为`, `此外`, `其中`, and `以及`, but replace them only when they sound unnatural in context.

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

### 4. Prepare for TTS

Without changing meaning:

- adjust punctuation, paragraphing, and `/` pauses
- make numbers, abbreviations, and symbols pronounceable
- split overlong scripts at natural content boundaries
- merge short scripts only when adjacent content is logically continuous

### 5. Generate and confirm a sample

Before the first full batch for a voice and rate combination, generate approximately one minute from representative content. Report the voice, rate, actual duration, and audio path.

Wait for user approval before batch generation. Reuse approval when the same project configuration has already been confirmed.

### 6. Generate ordered audio

For individual files, use:

```sh
.venv/bin/python -m edge_tts \
  --voice zh-HK-WanLungNeural \
  --rate=+20% \
  --file INPUT \
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

### 7. Verify the result

Use `ffprobe` to inspect duration, sample rate, bitrate, format, and size. Keep the original Microsoft MP3 unless the user or publishing platform explicitly requires 48 kHz.

Remember: 48 kbps bitrate is not 48 kHz sample rate. If conversion to 48 kHz is required, use `ffmpeg` and verify the converted file again.

## Output structure

Create:

```text
Book/
├── README.md
├── Script/
│   ├── 001.md
│   └── 002.md
└── Audio/
    ├── 001-章节标题.mp3
    └── 002-章节标题.mp3
```

Record the book title, source path, episode list, voice, rate, audio durations, generation date, and pronunciation notes in `Book/README.md`.

If the project already has an established output structure, keep it and document the mapping in its README.

## Failure handling

- If the source is missing, report the exact path and stop.
- If chapter structure is unclear, propose explainable manual boundaries.
- If `.venv` or `edge-tts` is missing, rebuild from `requirements-tts.txt`; do not install into a temporary directory.
- If synthesis fails, retry a limited number of times and retain completed audio.
- If WanLung is unavailable, list equivalent `zh-HK` Neural voices and ask before changing.
- If an episode falls outside 20–40 minutes, prefer a natural split or merge over exact timing.

## Completion checklist

- The episode plan was reviewed before full adaptation.
- Scripts preserve the author's content and position.
- Cantonese QA uses the required correction format.
- A sample was approved for a new configuration.
- Audio uses WanLung at 1.2x unless the user explicitly changes it.
- Each file represents one coherent 20–40 minute chapter.
- `ffprobe` verification passed.
- README, numbering, and file order are complete.
```

- [ ] **Step 3: Validate the frontmatter and required content**

Run:

```sh
.venv/bin/python - <<'PY'
from pathlib import Path

path = Path(".agents/skills/cantonese-audiobook-generator/SKILL.md")
text = path.read_text(encoding="utf-8")

assert text.startswith("---\n")
assert "\nname: cantonese-audiobook-generator\n" in text
assert "\ndescription:" in text
assert "zh-HK-WanLungNeural" in text
assert "rate=+20%" in text
assert "20–40 minutes" in text
assert "ffprobe" in text
assert "无需修改" in text
assert len(text.splitlines()) < 500
print("SKILL.md validation passed")
PY
```

Expected:

```text
SKILL.md validation passed
```

### Task 2: Add Lightweight Evaluation Prompts

**Files:**
- Create: `.agents/skills/cantonese-audiobook-generator/evals/evals.json`

**Interfaces:**
- Consumes: `.agents/skills/cantonese-audiobook-generator/SKILL.md`
- Produces: Three realistic test prompts for later qualitative or benchmark evaluation

- [ ] **Step 1: Create `evals/evals.json`**

Create:

```json
{
  "skill_name": "cantonese-audiobook-generator",
  "evals": [
    {
      "id": 1,
      "prompt": "项目里的 source/book.md 是一本约六万字的社会学非虚构作品，里面有三级标题。先不要改写全文，请根据听书体验规划成20到40分钟一集，并列出集数、标题、内容范围和预计时长。",
      "expected_output": "A reviewable episode plan produced before full adaptation, with boundaries based on complete arguments or sections and 20–40 minute estimates.",
      "files": []
    },
    {
      "id": 2,
      "prompt": "把下面这段普通话书面内容改成香港粤语知识节目讲稿，并做粤语质量检查。必须保留观点、数字和因果关系：‘因此，研究团队通过对1200名受访者进行调查，认为收入下降并不是消费减少的唯一原因。’",
      "expected_output": "Natural restrained Hong Kong Cantonese narration that preserves 1200, the research claim, and the causal qualification, followed by QA in the required correction format or 无需修改.",
      "files": []
    },
    {
      "id": 3,
      "prompt": "这本书的分集、雲龍男声和1.2倍语速我都已经确认过。请继续生成第003集，已有的001和002不要重做，并告诉我最终目录、文件名和验证命令。",
      "expected_output": "No repeated approval gate; uses the project .venv, WanLung +20%, skips existing non-empty MP3s, follows ordered naming, and includes ffprobe verification.",
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Validate the evaluation schema and IDs**

Run:

```sh
.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path(".agents/skills/cantonese-audiobook-generator/evals/evals.json")
data = json.loads(path.read_text(encoding="utf-8"))

assert data["skill_name"] == "cantonese-audiobook-generator"
assert [item["id"] for item in data["evals"]] == [1, 2, 3]
assert all(item["prompt"] for item in data["evals"])
assert all(item["expected_output"] for item in data["evals"])
assert all(item["files"] == [] for item in data["evals"])
print("evals.json validation passed")
PY
```

Expected:

```text
evals.json validation passed
```

### Task 3: Run Final Static Verification

**Files:**
- Verify: `.agents/skills/cantonese-audiobook-generator/SKILL.md`
- Verify: `.agents/skills/cantonese-audiobook-generator/evals/evals.json`
- Verify: `requirements-tts.txt`
- Verify: `.venv/bin/edge-tts`

**Interfaces:**
- Consumes: Outputs from Tasks 1 and 2
- Produces: Evidence that the project-local skill and its required TTS dependency are ready

- [ ] **Step 1: Check file layout**

Run:

```sh
find .agents/skills/cantonese-audiobook-generator -maxdepth 3 -type f | sort
```

Expected:

```text
.agents/skills/cantonese-audiobook-generator/SKILL.md
.agents/skills/cantonese-audiobook-generator/evals/evals.json
```

- [ ] **Step 2: Check the installed TTS version**

Run:

```sh
.venv/bin/edge-tts --version
```

Expected:

```text
edge-tts 7.2.8
```

- [ ] **Step 3: Scan for placeholders and accidental credential patterns**

Run:

```sh
rg -n 'TBD|TODO|PLACEHOLDER|api[_-]?key|password|secret|token' \
  .agents/skills/cantonese-audiobook-generator
```

Expected: no output and exit status 1.

- [ ] **Step 4: Confirm the skill stays within progressive-disclosure limits**

Run:

```sh
wc -l .agents/skills/cantonese-audiobook-generator/SKILL.md
```

Expected: fewer than 500 lines.

- [ ] **Step 5: Report completion**

Report the absolute paths of `SKILL.md` and `evals/evals.json`, the verified `edge-tts` version, and the exact kinds of tasks that trigger the skill. Do not claim that full audio generation was tested as part of this static skill installation.
