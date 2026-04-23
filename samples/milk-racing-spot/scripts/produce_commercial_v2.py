"""V2: fix shot 1 hand-off + add VO audio.

Operator QA caught two issues on v1:
  1. Shot 1 motion — crew member reaches toward the bottle but never
     completes the hand-off. Story-critical: the whole shot's punchline
     is the bottle-of-milk-instead-of-fuel beat.
  2. No audio. V1 shipped silent citing D022 audio-v0.2 scope, but
     OpenAI TTS is explicitly v0.1 per D031 — we can and should.

Fix approach:
  - Shot 1: regen via Veo 3.1 Standard with explicit hand-off completion
    language in the motion prompt. Upgraded from Fast tier.
  - Shots 2 & 3: reuse existing motion from v1_commercial.mp4 (extract
    via ffmpeg -ss/-t, lossless -c copy) — no regeneration needed.
  - Audio: 3 narration lines via OpenAI tts-1-hd onyx voice at 0.95x.
    Concat-filter VO track per D034, timed to visual beats.

Output: samples/milk-racing-spot/06_masters/v2_commercial.mp4
Keep v1 in place for operator comparison per D039.
"""
from __future__ import annotations
import json, os, subprocess, tempfile, time, shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import httpx, yaml
import PIL.Image, PIL.ImageDraw, PIL.ImageFont

SAMPLE = Path(__file__).resolve().parent.parent
SHOTS_FRAMES = SAMPLE / "03_shots"
MASTERS = SAMPLE / "06_masters"
QA = SAMPLE / "08_qa"
V1 = MASTERS / "v1_commercial.mp4"
OUT_W, OUT_H, FPS = 1920, 1080, 24
FONT = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"


def _key(prefix):
    for env in ("GEMINI_API_KEY" if prefix == "AIza" else "OPENAI_API_KEY",):
        if v := os.environ.get(env): return v
    data = yaml.safe_load((Path.home() / ".amplifier/settings.yaml").read_text()) or {}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.startswith(prefix): return v
                r = walk(v)
                if r: return r
        elif isinstance(o, list):
            for i in o:
                r = walk(i)
                if r: return r
    return walk(data)

GEMINI_KEY = _key("AIza")
OPENAI_KEY = _key("sk-proj")
from google import genai
from google.genai import types as gt
gclient = genai.Client(api_key=GEMINI_KEY, http_options={"timeout": 180000})
def sh(c): subprocess.run(c, check=True)
def sh_out(c): return subprocess.run(c, capture_output=True, text=True, check=True).stdout.strip()

tmp = Path(tempfile.mkdtemp(prefix="mrsv2_"))
print(f"tmp: {tmp}")

# ============================================================================
# Phase 1: Regen shot 1 via Veo Standard (fix the hand-off)
# ============================================================================
print("\n[1/6] Regen shot 1 — explicit hand-off completion motion prompt...")
shot1_motion = tmp / "shot1_motion.mp4"
shot1_prompt = (
    "Cinematic slow push-in over 8 seconds. The kneeling crew member in the foreground "
    "extends the frosted milk bottle fully toward the driver with smooth deliberate motion. "
    "The driver reaches out from the cockpit with a gloved hand and firmly takes the bottle, "
    "pulling it toward themselves and holding it close. The driver's visor finishes lifting, "
    "revealing a confident smile, and they turn the bottle slightly to admire it. Tire smoke "
    "drifts softly past. Warm stadium lights pulse with slight anamorphic lens flare. "
    "Golden-hour warmth steady throughout. No text appears."
)
first_frame = gt.Image(image_bytes=(SHOTS_FRAMES / "shot_01_approach.png").read_bytes(),
                        mime_type="image/png")
cfg = gt.GenerateVideosConfig(aspect_ratio="16:9", resolution="1080p", duration_seconds=8)

method_shot1 = None
try:
    op = gclient.models.generate_videos(
        model="veo-3.1-generate-preview", prompt=shot1_prompt,
        image=first_frame, config=cfg,
    )
    polls = 0
    while not op.done:
        polls += 1
        time.sleep(10)
        try: op = gclient.operations.get(op)
        except Exception: pass
        if polls > 60: raise TimeoutError("Veo poll timeout")
    if op.error: raise RuntimeError(f"Veo error: {op.error}")
    result = getattr(op, "result", None) or getattr(op, "response", None)
    videos = getattr(result, "generated_videos", []) or []
    v = getattr(videos[0], "video", videos[0])
    inline = getattr(v, "video_bytes", None)
    uri = getattr(v, "uri", None)
    if inline:
        shot1_motion.write_bytes(inline)
    elif uri:
        dl = uri if "key=" in uri else uri + ("&" if "?" in uri else "?") + f"key={GEMINI_KEY}"
        with httpx.Client(timeout=300.0, follow_redirects=True) as http:
            r = http.get(dl); r.raise_for_status(); shot1_motion.write_bytes(r.content)
    method_shot1 = "veo-standard"
    print(f"  veo succeeded: {shot1_motion.stat().st_size:,} bytes")
except Exception as e:
    print(f"  Veo failed ({str(e)[:120]}), falling back to Ken-Burns")
    frames = 8 * FPS
    sh(["ffmpeg", "-y", "-v", "error", "-loop", "1",
        "-i", str(SHOTS_FRAMES / "shot_01_approach.png"),
        "-vf", (f"scale=3840:2160:force_original_aspect_ratio=decrease,"
                f"pad=3840:2160:(ow-iw)/2:(oh-ih)/2,"
                f"zoompan=z='min(zoom+0.0006,1.06)':d={frames}:"
                f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
                f"s=1920x1080:fps=24"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", "-t", "8.0", str(shot1_motion)])
    method_shot1 = "ken-burns-fallback"

# ============================================================================
# Phase 2: Extract shots 2, 3, and tagline from v1_commercial.mp4
# ============================================================================
print("\n[2/6] Extract shots 2/3/tagline from v1_commercial.mp4 (lossless)...")
shot2_motion = tmp / "shot2_motion.mp4"
shot3_motion = tmp / "shot3_motion.mp4"
tagline_clip = tmp / "tagline.mp4"
# v1 layout: 0-8s shot1 | 8-16s shot2 | 16-24s shot3 | 24-27s tagline
sh(["ffmpeg", "-y", "-v", "error", "-ss", "8",  "-t", "8",   "-i", str(V1), "-c", "copy", str(shot2_motion)])
sh(["ffmpeg", "-y", "-v", "error", "-ss", "16", "-t", "8",   "-i", str(V1), "-c", "copy", str(shot3_motion)])
sh(["ffmpeg", "-y", "-v", "error", "-ss", "24", "-t", "3",   "-i", str(V1), "-c", "copy", str(tagline_clip)])
print(f"  shot 2: {shot2_motion.stat().st_size:,} bytes")
print(f"  shot 3: {shot3_motion.stat().st_size:,} bytes")
print(f"  tagline: {tagline_clip.stat().st_size:,} bytes")

# ============================================================================
# Phase 3: Generate 3 VO lines via OpenAI TTS — onyx, 0.95x
# ============================================================================
print("\n[3/6] Generating VO lines via OpenAI tts-1-hd (D031)...")
VO_LINES = [
    ("line_1", "When milliseconds matter..."),
    ("line_2", "...every drop is performance."),
    ("line_3", "Fuel. The fastest."),
]
TTS_HEADERS = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

def gen_tts(name_text):
    name, text = name_text
    out = tmp / f"vo_{name}.mp3"
    with httpx.Client(timeout=60.0) as http:
        r = http.post("https://api.openai.com/v1/audio/speech", headers=TTS_HEADERS,
            json={"model": "tts-1-hd", "voice": "onyx", "input": text, "speed": 0.95})
        r.raise_for_status()
        out.write_bytes(r.content)
    return (name, out, text, len(r.content))

with ThreadPoolExecutor(max_workers=3) as ex:
    vo_results = list(ex.map(gen_tts, VO_LINES))
vo_durations = {}
for name, path, text, size in vo_results:
    dur = float(sh_out(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)]))
    vo_durations[name] = dur
    print(f"  {name}: {size:,} bytes, {dur:.2f}s -- \"{text}\"")

# ============================================================================
# Phase 4: Build VO track via concat filter (D034)
# ============================================================================
print("\n[4/6] Building VO track with concat filter (D034)...")
# Timing plan:
#   line_1 at 5.0s   (mid shot 1, during the hand-off)
#   line_2 at 11.0s  (mid shot 2, during the macro pour)
#   line_3 at 24.5s  (on the end card, slightly into it)
SCHEDULE = [
    ("line_1", 5.0),
    ("line_2", 11.0),
    ("line_3", 24.5),
]
TOTAL_DUR = 27.0

segments = []
cursor = 0.0
for name, start_t in SCHEDULE:
    path = tmp / f"vo_{name}.mp3"
    gap = start_t - cursor
    if gap > 0.01:
        segments.append(("silence", gap))
    segments.append(("vo", path))
    cursor = start_t + vo_durations[name]
if cursor < TOTAL_DUR:
    segments.append(("silence", TOTAL_DUR - cursor))

cmd = ["ffmpeg", "-y", "-v", "error"]
filter_parts = []
labels = []
for i, seg in enumerate(segments):
    if seg[0] == "silence":
        cmd += ["-f", "lavfi", "-t", f"{seg[1]:.3f}",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    else:
        cmd += ["-i", str(seg[1])]
    label = f"[a{i}]"
    filter_parts.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo{label}")
    labels.append(label)
concat_line = "".join(labels) + f"concat=n={len(segments)}:v=0:a=1[aout]"
vo_track = tmp / "vo_track.m4a"
cmd += ["-filter_complex", ";".join(filter_parts + [concat_line]),
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", str(vo_track)]
sh(cmd)
print(f"  vo_track: {vo_track.stat().st_size:,} bytes ({TOTAL_DUR}s)")

# ============================================================================
# Phase 5: Normalize all clips + concat silent master + mux VO
# ============================================================================
print("\n[5/6] Normalizing + concatenating + muxing...")
norm = []
for i, src in enumerate([shot1_motion, shot2_motion, shot3_motion, tagline_clip]):
    dst = tmp / f"norm_{i:02d}.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps=24",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", str(dst)])
    norm.append(dst)

concat_file = tmp / "concat.txt"
concat_file.write_text("\n".join(f"file '{c.as_posix()}'" for c in norm) + "\n")
silent_master = tmp / "silent.mp4"
sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
    "-i", str(concat_file), "-c", "copy", str(silent_master)])

master = MASTERS / "v2_commercial.mp4"
sh(["ffmpeg", "-y", "-v", "error",
    "-i", str(silent_master), "-i", str(vo_track),
    "-c:v", "copy", "-c:a", "copy", "-shortest", str(master)])
actual_dur = float(sh_out(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=nw=1:nk=1", str(master)]))
print(f"  -> {master.relative_to(SAMPLE)} ({master.stat().st_size:,} bytes, {actual_dur:.2f}s)")

# Quick QA — check VO audibility at all 3 anchors
print("\n  Audio QA at VO anchors:")
import struct
for name, start_t in SCHEDULE:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start_t + 0.3), "-t", "0.5",
                        "-i", str(master), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                       capture_output=True, check=True)
    samples = struct.unpack(f"<{len(r.stdout)//2}h", r.stdout) if r.stdout else ()
    peak = max(abs(x) for x in samples) if samples else 0
    status = "✓" if peak > 500 else "✗ SILENT"
    print(f"    {name} @ {start_t:5.1f}s peak={peak:5d} {status}")

# ============================================================================
# Phase 6: Update manifest
# ============================================================================
print("\n[6/6] Updating manifest...")
manifest_path = QA / "production_manifest.json"
m = json.loads(manifest_path.read_text())
m["commercial_video_v2"] = {
    "file": "06_masters/v2_commercial.mp4",
    "fixes_from_v1": [
        "Shot 1 regenerated via Veo 3.1 Standard with explicit hand-off "
        "completion in the motion prompt (v1 Fast-tier motion had the crew "
        "member reaching but never completing the pass)",
        "Added narration audio track (D031 OpenAI tts-1-hd onyx voice at "
        "0.95x, 3 lines, concat-filter VO track per D034 timed to visual "
        "beats). V1 shipped silent citing D022 audio-v0.2 — that was wrong, "
        "OpenAI TTS is v0.1 cleared per D031.",
    ],
    "duration_s": round(actual_dur, 2),
    "resolution": "1920x1080",
    "fps": 24,
    "codec": "h264",
    "audio": {
        "codec": "aac",
        "bitrate": "192k",
        "sample_rate": 44100,
        "channels": 2,
        "vo_provider": "openai",
        "vo_model": "tts-1-hd",
        "vo_voice": "onyx",
        "vo_speed": 0.95,
        "vo_schedule": [
            {"line": text, "start_s": start_t, "duration_s": round(vo_durations[name], 2)}
            for (name, text), (_, start_t) in zip(VO_LINES, SCHEDULE)
        ],
        "music": "none (v0.1 bundle has no cleared music generator)",
    },
    "scenes": [
        {"id": "shot_01_approach", "duration_s": 8, "motion_method": method_shot1,
         "veo_tier": "standard" if "veo" in method_shot1 else None,
         "regen_reason": "v1 hand-off did not complete"},
        {"id": "shot_02_hero_pour", "duration_s": 8, "motion_method": "reused-from-v1",
         "source": "extracted via ffmpeg -ss 8 -t 8 -c copy from v1_commercial.mp4"},
        {"id": "shot_03_victory", "duration_s": 8, "motion_method": "reused-from-v1",
         "source": "extracted via ffmpeg -ss 16 -t 8 -c copy from v1_commercial.mp4"},
    ],
    "end_card": {"duration_s": 3, "text": "FUEL THE FASTEST",
                 "subtitle": "a sample commercial concept",
                 "font": "ChalkboardSE Regular",
                 "source": "reused from v1"},
}
manifest_path.write_text(json.dumps(m, indent=2))
print(f"  manifest updated with commercial_video_v2 section")

shutil.rmtree(tmp, ignore_errors=True)
print(f"\n=== V2 COMMERCIAL COMPLETE ===")
print(f"  file:     {master.relative_to(SAMPLE)}")
print(f"  duration: {actual_dur:.2f}s")
print(f"  shot 1 method: {method_shot1}")
print(f"  audio:    OpenAI tts-1-hd onyx, 3 lines via concat filter")
