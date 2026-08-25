# Cantonese Audiobook Generator

将普通话或书面中文非虚构作品改写成自然的香港粤语讲书稿，并使用 Microsoft `edge-tts` 的香港粤语声音生成 MP3 有声书。

项目重点是「编辑改写 + 发音预处理 + TTS 生成」这条流程：保留原书的观点、事实、数据、案例和论证顺序，再把文字调整为适合香港粤语朗读的表达。

## 项目定位

仓库目前包含：

- 项目级 Codex 技能：`.agents/skills/cantonese-audiobook-generator/`
- 粤语 TTS 发音词典和确定性文本预处理脚本
- `edge-tts` 依赖清单
- 批量生成入口脚本
- 设计文档和技能评测场景

批量入口 `generate_cantonese_audiobook.sh` 会调用
`cantonese_audiobook_tts/generate_all.py`。如果该目录未随当前 checkout 提供，需要先补齐生成器实现或使用已有项目文件；README 不把这个缺失的入口误认为已内置。

## 默认配置

| 项目 | 默认值 |
| --- | --- |
| TTS 引擎 | Microsoft `edge-tts` |
| 语言 | `zh-HK` |
| 声音 | `zh-HK-WanLungNeural`（雲龍） |
| 语速 | `+20%`，约 1.2 倍 |
| 格式 | MP3 |
| 分集边界 | 每个原书章节对应一个最终讲稿和 MP3 |
| 语气 | 平静、专业，适合长时间收听 |

## 环境准备

项目建议使用 Python 虚拟环境，并需要 `ffprobe` 检查生成音频。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-tts.txt
```

依赖版本位于 [`requirements-tts.txt`](requirements-tts.txt)，当前包括：

- `edge-tts==7.2.8`
- `opencc-python-reimplemented==0.1.7`

检查 TTS 工具是否可用：

```sh
.venv/bin/edge-tts --list-voices | grep 'zh-HK'
ffprobe -version
```

## 推荐工作流程

### 1. 指定书籍并确认章节规划

把待处理的书放在 `books/` 下，并提供明确路径。先按照原书的章节结构列出章节编号、标题和原文范围，再开始改写。不要仅按字符数拆分或合并原书章节。

### 2. 改写香港粤语讲稿

讲稿应接近香港知识节目或专业讲书主播的表达：约七成口语粤语、三成书面表达。需要保留原作者的立场、限定条件、数据和因果关系，不添加原文没有的观点。

建议将人工审核用的阅读稿保存到：

```text
Book/Script/001-cantonese.md
```

质量检查有修改时，使用以下格式：

```text
原句：

修改：

原因：
```

没有问题时写 `无需修改`。

### 3. 生成独立的 TTS 输入稿

不要直接覆盖 `Script/` 阅读稿。使用预处理脚本生成只供 `edge-tts` 使用的副本：

```sh
.venv/bin/python \
  .agents/skills/cantonese-audiobook-generator/scripts/normalize_cantonese_tts.py \
  Book/Script/001-cantonese.md \
  Book/TTS/001-edge.txt \
  --book-dictionary Book/TTS/pronunciation-dictionary.tsv
```

脚本会：

- 应用项目内置的粤语发音词典
- 应用书籍专用词典覆盖项
- 优先匹配较长词组，并且每个替换只执行一次
- 将阅读稿中的 `/` 停顿符转换为标点
- 将 URL 前缀转换成可朗读的文字
- 在输出仍含 `/` 时停止，避免 TTS 把斜线读出来

项目内置词典位于 [`cantonese-tts-pronunciations.tsv`](.agents/skills/cantonese-audiobook-generator/references/cantonese-tts-pronunciations.tsv)，其中包含强制替换 `噉 → 咁`。书籍专用词典使用 UTF-8 TSV，格式为：

```text
# source	replacement	note
```

### 4. 试听后批量生成

首次使用某个声音和语速时，先生成约一分钟试听并确认。单个章节可使用：

```sh
.venv/bin/python -m edge_tts \
  --voice zh-HK-WanLungNeural \
  --rate=+20% \
  --file Book/TTS/001-edge.txt \
  --write-media Book/Audio/001-章节标题.mp3
```

当前固定批量入口为：

```sh
./generate_cantonese_audiobook.sh
```

该入口依赖 `cantonese_audiobook_tts/generate_all.py`，并使用项目的 `.venv`。已有且非空的 MP3 应跳过，以便在中断后继续生成；不要静默更换声音。

### 5. 验证音频并生成播放列表

生成后使用 `ffprobe` 检查格式、时长、采样率、码率和文件大小：

```sh
ffprobe -v error \
  -show_entries format=duration,size,bit_rate \
  -show_entries stream=codec_name,sample_rate,channels \
  -of default=noprint_wrappers=1 \
  Book/Audio/001-章节标题.mp3
```

确认所有章节 MP3 都存在、非空且通过验证后，再在同一个 `Audio/` 目录生成 UTF-8 M3U 播放列表。列表只应包含最终章节音频，不要加入试听文件、临时分块或中间文件：

```text
#EXTM3U
001-章节标题.mp3
002-章节标题.mp3
```

## 推荐输出结构

```text
Book/
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

每本书的 README 建议记录书名、源文件、章节清单、声音、语速、音频时长、生成日期、词典替换和未解决的读音问题。

## 重要注意事项

- `Script/` 是供人审核的阅读稿；`TTS/` 是供合成的独立输入稿，两者不要混用。
- `edge-tts` 的纯文本 CLI 可能会把 `/` 读成“斜线”，合成前必须确认 TTS 输入不含 `/`。
- 48 kbps 是码率，48 kHz 是采样率，两者不是同一个参数。除非播放器或发行平台明确要求，不要重复转码。
- 如果某个词无法通过安全的同义改写解决读音问题，应保留阅读稿、记录问题，并在更换 TTS 引擎或 SDK 前确认。
- `.env`、Cookie、API key、令牌等敏感信息不得写入代码、日志、讲稿或 README。

## 相关文件

- [`SKILL.md`](.agents/skills/cantonese-audiobook-generator/SKILL.md)：完整工作流程、质量标准和错误处理
- [`normalize_cantonese_tts.py`](.agents/skills/cantonese-audiobook-generator/scripts/normalize_cantonese_tts.py)：TTS 输入预处理脚本
- [`cantonese-tts-pronunciations.tsv`](.agents/skills/cantonese-audiobook-generator/references/cantonese-tts-pronunciations.tsv)：内置发音词典
- [`requirements-tts.txt`](requirements-tts.txt)：Python 依赖
- [`generate_cantonese_audiobook.sh`](generate_cantonese_audiobook.sh)：批量生成入口

