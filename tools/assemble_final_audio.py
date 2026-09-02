from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "cantonese_audiobook_tts" / "非对称风险"
AUDIO = BOOK / "Audio"
FINAL = BOOK / "FinalAudio"


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    FINAL.mkdir(exist_ok=True)
    # Recommendation 1 has a distinct name; all remaining numbered units use NNN-edge.
    sources = {"001-recommendation": AUDIO / "001-recommendation-edge.mp3"}
    for n in range(2, 34):
        key = f"{n:03d}"
        full = AUDIO / f"{key}-edge.mp3"
        if full.exists() and full.stat().st_size > 10000:
            sources[key] = full
            continue
        parts = sorted(AUDIO.glob(f"{key}-[0-9][0-9][0-9]-edge.mp3"))
        if not parts:
            print(f"MISSING {key}")
            continue
        concat = FINAL / f".{key}.concat.txt"
        concat.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
        out = FINAL / f"{key}.mp3"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(out)])
        concat.unlink()
        sources[key] = out
        print(f"MERGED {key} ({len(parts)} parts)")
    for key, src in sources.items():
        out = FINAL / f"{key}.mp3"
        if src != out:
            out.write_bytes(src.read_bytes())
    ordered = ["001-recommendation"] + [f"{n:03d}" for n in range(2, 34)]
    missing = [key for key in ordered if not (FINAL / f"{key}.mp3").exists()]
    if missing:
        raise SystemExit(f"Missing final units: {', '.join(missing)}")
    playlist = BOOK / "非对称风险.m3u"
    playlist.write_text("#EXTM3U\n" + "\n".join(f"FinalAudio/{key}.mp3" for key in ordered) + "\n", encoding="utf-8")
    print(f"PLAYLIST {playlist}")
    print(f"FINAL_COUNT {len(sources)}")


if __name__ == "__main__":
    main()
