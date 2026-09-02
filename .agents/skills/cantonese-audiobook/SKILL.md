---
name: cantonese-audiobook
description: 把普通话 EPUB 电子书改写成地道香港粤语阅读稿，并用 edge-tts 雲龍生成有声书。当用户要求「电子书转粤语有声书」「普转粤」「粤语配音/朗读/读物」时使用。
---

# 粤语有声书生成（普通话 EPUB → 香港粤语）

## 适用范围

本 skill 适用于当前 Codex 项目：所有命令从仓库根目录运行，使用项目 `.venv`，书籍工作目录为 `cantonese_audiobook_tts/<书名>/`。讲稿改写、校对和修订由当前 Codex 模型直接完成；不调用外部改写模型，也不要求 API key。

TTS 默认使用 Microsoft `edge-tts` 的香港粤语声音 `zh-HK-WanLungNeural`（雲龍），MiniMax 等其他引擎只有在用户明确同意后才能切换。

## 环境

- 项目根目录：本仓库根目录（所有命令均从此处运行）
- 虚拟环境：`.venv/`；依赖见 `requirements-tts.txt`
- 输入 EPUB 放在 `books/`，生成内容放在 `cantonese_audiobook_tts/<书名>/`
- 生成前确认：`.venv/bin/edge-tts --list-voices | grep 'zh-HK'` 和 `ffprobe -version`

## 流程

### 1. 提取并确认章节

先读取 EPUB 的 spine/目录和正文，按原书章节边界建立 `source/NNN-<标题>-source.md`。不要仅按字符数拆分或合并章节。提取后先向用户报告章节切分，确认无误再批量改写。

单章测试可以只建立一个 `source/001-<标题>-source.md`，并在书目录 README 中记录原始 EPUB 路径和测试范围。

### 2. 用 Codex 改写粤语讲稿

当前 Codex 模型直接将源稿改写为约七成口语、三成书面的香港粤语讲书稿。讲稿必须使用香港繁体字，不得把简体字稿直接交给 TTS。保留原作者的观点、事实、数据、案例、限定条件、因果关系、人名和书名；不添加原文没有的内容。输出到 `Script/NNN-cantonese.md`，不要覆盖 `source/`。

先用项目虚拟环境中的 OpenCC 做简体到繁体转换，再由 Codex 人工校正粤语字形和用词：`OpenCC('s2t')`；例如 `客户→客戶`、`税务→稅務`、`想象→想像`、`游说→遊說`，并将粤语常用的 `係、嘅、冇、佢、啲、咗` 等字形统一。人工检查普通话残留（的/了/把/被等）、粤语语法、自然度、数字与专名完整性。需要修改时保留修改记录；没有问题写明“无需修改”。

### 3. 准备独立 TTS 输入

`TTS/NNN-edge.txt` 是给合成器的独立副本，不能直接把 `Script/` 当作可变的 TTS 输入。生成 TTS 输入前，再用 OpenCC `s2t` 检查转换结果为空差异；若仍有简体或异体字，先修正讲稿再合成。合成前同时处理 `/` 停顿符、URL 和需要特别读音的词，确保最终输入不含会被读成“斜线”的 `/`。如果项目内有发音预处理脚本，优先使用它；没有则由 Codex 做最小、可审计的文本预处理，并保留阅读稿原文。

### 4. 生成单章音频

```sh
.venv/bin/python -m edge_tts \
  --voice zh-HK-WanLungNeural \
  --rate=+20% \
  --file cantonese_audiobook_tts/<书名>/TTS/001-edge.txt \
  --write-media cantonese_audiobook_tts/<书名>/Audio/001-<章节标题>.mp3
```

首次测试先生成约一分钟片段试听。未得到用户确认前，不生成整本书，也不删除或覆盖已有音频。若网络或 `edge-tts` 失败，记录错误并保留稿件，不伪造音频完成状态。

### 5. 验证

```sh
ffprobe -v error \
  -show_entries format=duration,size,bit_rate \
  -show_entries stream=codec_name,sample_rate,channels \
  -of default=noprint_wrappers=1 \
  cantonese_audiobook_tts/<书名>/Audio/001-<章节标题>.mp3
```

确认 MP3 存在、非空、可被 ffprobe 读取、时长与稿件体量合理，并向用户报告实际输出路径和试听结果。完整书籍验收后才在 `Audio/` 内创建只含最终章节文件名的 UTF-8 M3U 播放列表。

## 输出结构

```text
cantonese_audiobook_tts/<书名>/
├── README.md
├── source/  NNN-<章节>-source.md
├── Script/  NNN-cantonese.md
├── TTS/     NNN-edge.txt
└── Audio/   NNN-<章节>.mp3
```

`.env`、Cookie、API key、令牌等敏感信息不得写入代码、日志、讲稿或 README。不得把测试一章宣称为整本书已完成。
