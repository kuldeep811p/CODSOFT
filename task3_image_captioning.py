"""
CODSOFT AI Internship — Task 3 UPGRADED
Image Captioning — Advanced Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Features:
  ✦ Batch captioning — process an entire folder at once
  ✦ Multiple caption candidates per image (beam search)
  ✦ Save captions to JSON / TXT report
  ✦ Image metadata display (size, format, mode)
  ✦ Caption length control (short / medium / detailed)
  ✦ Progress bar for batch mode
  ✦ Supports local files, URLs, and glob patterns
  ✦ Auto GPU/CPU selection

Requirements:
    pip install torch torchvision transformers pillow requests tqdm
"""

import os, sys, json, time
from pathlib import Path
from io import BytesIO
from datetime import datetime

# ── Install check ───
try:
    from transformers import AutoProcessor, AutoModelForCausalLM
    from PIL import Image
    import requests, torch
    from tqdm import tqdm
except ImportError:
    print("Installing dependencies...")
    os.system("pip install transformers pillow requests torch torchvision tqdm --quiet")
    from transformers import AutoProcessor, AutoModelForCausalLM
    from PIL import Image
    import requests, torch
    from tqdm import tqdm

# ── Model ──────────────────────────────────────────────────
MODEL_NAME   = "microsoft/git-base-coco"
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"
_processor   = None
_model       = None

LENGTH_TOKENS = {"short": 20, "medium": 40, "detailed": 80}

def load_model():
    global _processor, _model
    if _model is None:
        print(f"📦 Loading model ({MODEL_NAME}) on {DEVICE.upper()}...")
        _processor = AutoProcessor.from_pretrained(MODEL_NAME)
        _model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(DEVICE)
        _model.eval()
        print("✅ Model ready!\n")

# ── Core Caption Generator ─────────────────────────────────
def caption_image(
    image: Image.Image,
    length: str = "medium",
    num_captions: int = 1,
) -> list[str]:
    """
    Returns a list of caption strings.
    num_captions > 1 uses beam-search diversity sampling.
    """
    load_model()
    max_tokens = LENGTH_TOKENS.get(length, 40)
    pv = _processor(images=image, return_tensors="pt").pixel_values.to(DEVICE)

    with torch.no_grad():
        if num_captions == 1:
            ids = _model.generate(pixel_values=pv, max_new_tokens=max_tokens)
        else:
            ids = _model.generate(
                pixel_values=pv,
                max_new_tokens=max_tokens,
                num_beams=max(num_captions, 4),
                num_return_sequences=num_captions,
                diversity_penalty=0.5,
                num_beam_groups=min(num_captions, 4),
            )

    return _processor.batch_decode(ids, skip_special_tokens=True)

# ── Image Loaders ──────────────────────────────────────────
def load_from_path(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")

def load_from_url(url: str) -> Image.Image:
    r = requests.get(url, timeout=15); r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGB")

def image_info(img: Image.Image) -> dict:
    return {"size": f"{img.width}×{img.height}", "mode": img.mode,
            "format": getattr(img, "format", "unknown")}

# ── Single Image ───────────────────────────────────────────
def caption_one(source: str, length="medium", num_captions=1) -> dict:
    """Caption one image from path or URL. Returns result dict."""
    t0 = time.time()
    if source.startswith("http"):
        img = load_from_url(source)
    else:
        img = load_from_path(source)

    captions = caption_image(img, length=length, num_captions=num_captions)
    elapsed  = round(time.time() - t0, 2)

    return {
        "source":   source,
        "info":     image_info(img),
        "captions": captions,
        "length":   length,
        "time_sec": elapsed,
    }

# ── Batch Processing ───────────────────────────────────────
def caption_batch(folder: str, extensions=(".jpg",".jpeg",".png",".webp"),
                  length="medium", output_json="captions.json") -> list[dict]:
    """Caption all images in a folder and save results."""
    load_model()
    paths = [p for p in Path(folder).iterdir()
             if p.suffix.lower() in extensions]
    if not paths:
        print(f"No images found in {folder}"); return []

    results = []
    print(f"📂 Processing {len(paths)} image(s) from '{folder}'...\n")
    for path in tqdm(paths, desc="Captioning", unit="img"):
        try:
            res = caption_one(str(path), length=length)
            results.append(res)
        except Exception as e:
            results.append({"source": str(path), "error": str(e)})

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Done! Results saved to '{output_json}'")
    return results

# ── Text Report ────────────────────────────────────────────
def save_txt_report(results: list[dict], path="captions_report.txt"):
    with open(path, "w") as f:
        f.write(f"Image Captioning Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            f.write(f"Source : {r['source']}\n")
            if "error" in r:
                f.write(f"Error  : {r['error']}\n")
            else:
                f.write(f"Size   : {r['info']['size']}\n")
                f.write(f"Time   : {r['time_sec']}s\n")
                for i, cap in enumerate(r["captions"], 1):
                    f.write(f"Cap {i}  : {cap}\n")
            f.write("\n" + "-"*60 + "\n\n")
    print(f"📄 Text report saved to '{path}'")

# ── Pretty Print ───────────────────────────────────────────
def display_result(res: dict):
    if "error" in res:
        print(f"  ❌ Error: {res['error']}")
        return
    info = res["info"]
    print(f"  📷 Source  : {res['source']}")
    print(f"  📐 Size    : {info['size']}  Mode: {info['mode']}")
    print(f"  ⏱  Time    : {res['time_sec']}s")
    for i, cap in enumerate(res["captions"], 1):
        label = "📝 Caption" if len(res["captions"]) == 1 else f"📝 Caption {i}"
        print(f"  {label}: {cap}")

# ── Demo URLs ──────────────────────────────────────────────
DEMO_URLS = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg", "Cat"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Cute_dog.jpg/320px-Cute_dog.jpg", "Dog"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Above_Gotham.jpg/320px-Above_Gotham.jpg", "City"),
]

# ── CLI ─────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  🖼️  Image Captioning  —  CODSOFT AI Task 3")
    print("=" * 55)

    while True:
        print("\nOptions:")
        print("  1  Caption a single image (file or URL)")
        print("  2  Caption multiple candidates (beam search)")
        print("  3  Batch caption an entire folder")
        print("  4  Run demo on sample images")
        print("  5  Exit")

        ch = input("\nChoice: ").strip()

        if ch == "1":
            src    = input("  File path or URL: ").strip()
            length = input("  Length (short / medium / detailed) [medium]: ").strip() or "medium"
            print("  ⏳ Generating...")
            try:
                res = caption_one(src, length=length)
                print(); display_result(res)
            except Exception as e:
                print(f"  ❌ {e}")

        elif ch == "2":
            src    = input("  File path or URL: ").strip()
            n      = int(input("  Number of captions (2-4) [3]: ").strip() or "3")
            length = input("  Length (short / medium / detailed) [medium]: ").strip() or "medium"
            print("  ⏳ Generating candidates...")
            try:
                res = caption_one(src, length=length, num_captions=n)
                print(); display_result(res)
            except Exception as e:
                print(f"  ❌ {e}")

        elif ch == "3":
            folder = input("  Folder path: ").strip()
            length = input("  Length (short / medium / detailed) [medium]: ").strip() or "medium"
            out    = input("  Output JSON file [captions.json]: ").strip() or "captions.json"
            results = caption_batch(folder, length=length, output_json=out)
            if results:
                save_txt_report(results)
                print(f"\n  Summary ({len(results)} images):")
                for r in results: display_result(r); print()

        elif ch == "4":
            load_model()
            print("\n  🎬 Demo on sample images...\n")
            all_res = []
            for url, label in DEMO_URLS:
                print(f"  ▶ {label}")
                try:
                    res = caption_one(url, length="medium")
                    display_result(res); print()
                    all_res.append(res)
                except Exception as e:
                    print(f"  ❌ {e}\n")
            if all_res:
                save_txt_report(all_res, "demo_captions_report.txt")

        elif ch == "5":
            print("Goodbye! 👋"); break
        else:
            print("  Invalid option.")

if __name__ == "__main__":
    # CLI shortcut: python task3.py <path_or_url>
    if len(sys.argv) > 1:
        load_model()
        res = caption_one(sys.argv[1])
        display_result(res)
    else:
        main()
