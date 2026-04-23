"""Turn the 3 stills into a stitched commercial.

- Veo 3.1 motion on each first-frame (Standard/Fast/Standard).
  Ken-Burns fallback per shot if Veo quota is exhausted (D032/D043).
- 3-second tagline end-card (black bg, ChalkboardSE white).
- Normalize all 4 clips to 1920x1080 @ 24fps and concat.
- Save as samples/milk-racing-spot/06_masters/v1_commercial.mp4.
- Silent (audio is v0.2 scope per D022).
"""
from __future__ import annotations
import json, os, subprocess, tempfile, time, shutil
from pathlib import Path
import httpx, yaml
import PIL.Image, PIL.ImageDraw, PIL.ImageFont

SAMPLE = Path(__file__).resolve().parent.parent
SHOTS_FRAMES = SAMPLE / "03_shots"
MASTERS = SAMPLE / "06_masters"
QA = SAMPLE / "08_qa"
MOTION = SAMPLE / "_motion"
MASTERS.mkdir(parents=True, exist_ok=True)
MOTION.mkdir(parents=True, exist_ok=True)

OUT_W, OUT_H, FPS = 1920, 1080, 24
FONT = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"

def gemini_key():
    if v := os.environ.get("GEMINI_API_KEY"): return v
    data = yaml.safe_load((Path.home() / ".amplifier/settings.yaml").read_text()) or {}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.startswith("AIza"): return v
                r = walk(v)
                if r: return r
        elif isinstance(o, list):
            for i in o:
                r = walk(i)
                if r: return r
    return walk(data)

KEY = gemini_key()
from google import genai
from google.genai import types as gt
client = genai.Client(api_key=KEY, http_options={"timeout": 180000})
def sh(c): subprocess.run(c, check=True)

SCENES = [
    {"id": "shot_01_approach", "png": SHOTS_FRAMES / "shot_01_approach.png", "tier": "fast",
     "prompt": ("Slow push-in. Tire smoke drifts slowly past the camera. The kneeling crew member "
                "steadies the frosted bottle of milk. The driver's head turns subtly toward the bottle "
                "as the visor lifts. Warm stadium lights flicker gently. Slight anamorphic lens flare "
                "pulses. Golden-hour warmth steady throughout. No text appears.")},
    {"id": "shot_02_hero_pour", "png": SHOTS_FRAMES / "shot_02_hero_pour.png", "tier": "standard",
     "prompt": ("Milk continues pouring in smooth slow motion from the chrome pitcher into the "
                "matte-black sports bottle. Droplets suspend mid-air and slowly fall. The crown splash "
                "at the bottle's lip spreads outward in slow waves. Condensation beads glisten. "
                "Background heat haze shimmers softly. Camera holds still on macro focus. No text appears.")},
    {"id": "shot_03_victory", "png": SHOTS_FRAMES / "shot_03_victory.png", "tier": "standard",
     "prompt": ("The arc of white milk cascades upward then rains down in slow-motion droplets, "
                "catching warm stadium spotlights. Confetti continues drifting down. The driver's "
                "triumphant grin widens slightly. The camera pushes in slowly. Stadium spotlights "
                "pulse warmth. Cheering crowd silhouettes sway in the background. No text appears.")},
]

TIER_MODELS = {"standard": "veo-3.1-generate-preview", "fast": "veo-3.1-fast-generate-preview"}

def try_veo(scene):
    out = MOTION / f"{scene['id']}.mp4"
    if out.exists() and out.stat().st_size > 100_000:
        print(f"    motion already exists ({out.stat().st_size:,} bytes), skipping")
        return True, "cached"
    first_frame = gt.Image(image_bytes=scene["png"].read_bytes(), mime_type="image/png")
    cfg = gt.GenerateVideosConfig(aspect_ratio="16:9", resolution="1080p", duration_seconds=8)
    try:
        op = client.models.generate_videos(
            model=TIER_MODELS[scene["tier"]], prompt=scene["prompt"],
            image=first_frame, config=cfg)
    except Exception as e:
        print(f"    Veo submit failed: {str(e)[:140]}")
        return False, "veo-failed"
    polls = 0
    while not op.done:
        polls += 1
        time.sleep(10)
        try: op = client.operations.get(op)
        except Exception: pass
        if polls > 60:
            return False, "poll-timeout"
    if op.error:
        print(f"    Veo error: {str(op.error)[:140]}")
        return False, "veo-error"
    result = getattr(op, "result", None) or getattr(op, "response", None)
    videos = getattr(result, "generated_videos", []) or []
    if not videos: return False, "no-video"
    v = getattr(videos[0], "video", videos[0])
    inline = getattr(v, "video_bytes", None)
    uri = getattr(v, "uri", None)
    if inline:
        out.write_bytes(inline)
    elif uri:
        dl = uri if "key=" in uri else uri + ("&" if "?" in uri else "?") + f"key={KEY}"
        with httpx.Client(timeout=300.0, follow_redirects=True) as http:
            r = http.get(dl); r.raise_for_status(); out.write_bytes(r.content)
    else:
        return False, "no-bytes"
    return True, f"veo-{scene['tier']}"


def ken_burns(scene, duration=8.0):
    out = MOTION / f"{scene['id']}.mp4"
    frames = int(duration * FPS)
    sh(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(scene["png"]),
        "-vf", (f"scale=3840:2160:force_original_aspect_ratio=decrease,"
                f"pad=3840:2160:(ow-iw)/2:(oh-ih)/2,"
                f"zoompan=z='min(zoom+0.0006,1.06)':d={frames}:"
                f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
                f"s=1920x1080:fps=24"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", "-t", f"{duration:.3f}", str(out)])


print("[1/4] Generating motion (Veo attempts, Ken-Burns fallback)...")
scene_results = []
for s in SCENES:
    print(f"  -> {s['id']} (tier={s['tier']})")
    ok, method = try_veo(s)
    if not ok:
        print(f"     falling back to Ken-Burns (D032/D043)")
        ken_burns(s, duration=8.0)
        method = "ken-burns-fallback"
    scene_results.append({"id": s["id"], "method": method, "tier": s["tier"]})
    print(f"     method: {method}")

print("\n[2/4] Rendering tagline end-card (3s)...")
tmp = Path(tempfile.mkdtemp(prefix="mrs_"))
img = PIL.Image.new("RGB", (OUT_W, OUT_H), (12, 12, 14))
d = PIL.ImageDraw.Draw(img)
tag_font = PIL.ImageFont.truetype(FONT, 148, index=1)
sub_font = PIL.ImageFont.truetype(FONT, 44, index=1)
tag = "FUEL THE FASTEST"
sub = "a sample commercial concept"
tb = d.textbbox((0,0), tag, font=tag_font)
sb = d.textbbox((0,0), sub, font=sub_font)
ty = OUT_H // 2 - (tb[3]-tb[1]) // 2 - 40
sy = ty + (tb[3]-tb[1]) + 70
d.text(((OUT_W-(tb[2]-tb[0]))//2 - tb[0], ty - tb[1]), tag, font=tag_font, fill=(248, 242, 230))
d.text(((OUT_W-(sb[2]-sb[0]))//2 - sb[0], sy - sb[1]), sub, font=sub_font, fill=(168, 156, 138))
tagline_png = tmp / "tagline.png"
img.save(tagline_png)
tagline_mp4 = tmp / "tagline.mp4"
sh(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(tagline_png),
    "-vf", "fps=24", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "-an", "-t", "3.0", str(tagline_mp4)])
print("  done")

print("\n[3/4] Normalize + concat...")
norm = []
for i, s in enumerate(SCENES):
    src = MOTION / f"{s['id']}.mp4"
    dst = tmp / f"norm_{i:02d}.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps=24",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", str(dst)])
    norm.append(dst)
dst_tag = tmp / "norm_03_tag.mp4"
sh(["ffmpeg", "-y", "-v", "error", "-i", str(tagline_mp4),
    "-vf", "scale=1920:1080,fps=24",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "-an", str(dst_tag)])
norm.append(dst_tag)

cfile = tmp / "concat.txt"
cfile.write_text("\n".join(f"file '{c.as_posix()}'" for c in norm) + "\n")
master = MASTERS / "v1_commercial.mp4"
sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
    "-i", str(cfile), "-c", "copy", str(master)])
dur_out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nw=1:nk=1", str(master)], capture_output=True, text=True)
actual_dur = float(dur_out.stdout.strip())
print(f"  -> 06_masters/v1_commercial.mp4 ({master.stat().st_size:,} bytes, {actual_dur:.2f}s)")

print("\n[4/4] Updating manifest...")
manifest_path = QA / "production_manifest.json"
m = json.loads(manifest_path.read_text())
m["commercial_video"] = {
    "file": "06_masters/v1_commercial.mp4",
    "duration_s": round(actual_dur, 2),
    "resolution": "1920x1080",
    "fps": 24,
    "codec": "h264",
    "audio": None,
    "audio_note": "silent — audio is v0.2 scope per D022",
    "scenes": [
        {"id": s["id"], "duration_s": 8, "motion_method": r["method"],
         "veo_tier": r["tier"] if "veo" in r["method"] else None}
        for s, r in zip(SCENES, scene_results)],
    "end_card": {"duration_s": 3, "text": "FUEL THE FASTEST",
                 "subtitle": "a sample commercial concept",
                 "font": "ChalkboardSE Regular"},
}
manifest_path.write_text(json.dumps(m, indent=2))
print("  manifest updated")

shutil.rmtree(tmp, ignore_errors=True)
# Clean up the motion working dir — ship only the final master
shutil.rmtree(MOTION, ignore_errors=True)

print("\n=== COMMERCIAL PRODUCTION COMPLETE ===")
print(f"  file:     {master.relative_to(SAMPLE)}")
print(f"  duration: {actual_dur:.2f}s")
print(f"  motions:  {[(r['id'], r['method']) for r in scene_results]}")
