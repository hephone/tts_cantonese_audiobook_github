#!/usr/bin/env python3
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "cantonese_audiobook_tts" / "非对称风险"
TTS = BOOK / "TTS"
AUDIO = BOOK / "Audio"
VOICE = "zh-HK-WanLungNeural"

async def one(src: Path, sem: asyncio.Semaphore):
    out = AUDIO / (src.stem + ".mp3")
    if out.exists() and out.stat().st_size > 10000:
        return f"skip {src.name}"
    async with sem:
        proc = await asyncio.create_subprocess_exec(
            str(ROOT / ".venv/bin/python"), "-m", "edge_tts",
            "--voice", VOICE, "--rate=+20%", "--file", str(src),
            "--write-media", str(out),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, err = await asyncio.wait_for(proc.communicate(), timeout=180)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"TIMEOUT {src.name}"
        if proc.returncode:
            return f"FAIL {src.name}: {err.decode(errors='replace')[-300:]}"
        return f"ok {src.name}"

async def main():
    AUDIO.mkdir(exist_ok=True)
    files = sorted(TTS.glob("*.txt"))
    files = [p for p in files if not p.name.startswith("pilot-")]
    sem = asyncio.Semaphore(3)
    for result in await asyncio.gather(*(one(p, sem) for p in files)):
        print(result, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
