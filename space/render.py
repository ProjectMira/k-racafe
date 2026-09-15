#!/usr/bin/env python3
"""Render the kōra space views with an image model (Gemini or OpenAI).

    python3 space/render.py                 # all ten views, overview first
    python3 space/render.py 1               # just the overview
    python3 space/render.py 3 5 --backend openai --quality medium

Reads the prompts from render-prompts.md (scene lock + view), writes
renders/NN-name.jpg (or .png, whatever the API returns) plus a .json sidecar recording the exact prompt, model
and references used.  Needs GEMINI_API_KEY (default backend) or OPENAI_API_KEY
in the environment.

Consistency: view 1 attaches floor-plan.png as a layout reference; every
other view attaches floor-plan.png and the finished view 1 render, so the
set reads as one café.  --no-refs turns that off.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "renders"
API = "https://api.openai.com/v1/images"


def load_prompts():
    md = (HERE / "render-prompts.md").read_text(encoding="utf-8")
    lock, views = "", {}
    for sec in re.split(r"\n## ", md)[1:]:
        title, _, body = sec.partition("\n")
        q = " ".join((l[2:] if l.startswith("> ") else l[1:]).strip()
                     for l in body.splitlines() if l.startswith(">"))
        if title.startswith("Scene lock"):
            lock = q
        elif title[:1].isdigit() and q:
            n, _, name = title.partition(" · ")
            views[int(n)] = (name.strip(), q)
    return lock, views


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]


def size_for(text):
    return "1024x1536" if "2:3" in text else "1536x1024"


def call(args):
    r = subprocess.run(["curl", "-sS", "--max-time", "600", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"curl failed: {r.stderr[:500]}")
    try:
        j = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"bad response: {r.stdout[:500]}")
    if "error" in j:
        sys.exit(f"API error: {j['error'].get('message')}")
    return j


GEMINI = "https://generativelanguage.googleapis.com/v1beta/models"


def generate_gemini(model, prompt, size, refs):
    """One image via generateContent; refs go in as inline PNGs before the text."""
    import urllib.request
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY not set")
    parts = [{"inline_data": {"mime_type": "image/png",
                              "data": base64.b64encode(Path(r).read_bytes()).decode()}} for r in refs]
    parts.append({"text": prompt})
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": "2:3" if size == "1024x1536" else "3:2"}}}
    if "pro" in model:
        body["generationConfig"]["imageConfig"]["imageSize"] = "2K"
    req = urllib.request.Request(f"{GEMINI}/{model}:generateContent", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            j = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini error {e.code}: {e.read()[:600].decode(errors='replace')}")
    for cand in j.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob:
                mime = blob.get("mimeType") or blob.get("mime_type") or "image/png"
                return base64.b64decode(blob["data"]), j.get("usageMetadata"), mime
    sys.exit(f"no image in response: {json.dumps(j)[:600]}")


def generate(model, prompt, size, quality, refs):
    key = os.environ.get("OPENAI_API_KEY") or sys.exit("OPENAI_API_KEY not set")
    auth = ["-H", f"Authorization: Bearer {key}"]
    if refs:
        files = []
        for r in refs:
            files += ["-F", f"image[]=@{r}"]
        j = call([f"{API}/edits", *auth,
                  "--form-string", f"model={model}", "--form-string", f"prompt={prompt}",
                  "--form-string", f"size={size}", "--form-string", f"quality={quality}",
                  "--form-string", "n=1", *files])
    else:
        body = json.dumps({"model": model, "prompt": prompt, "size": size, "quality": quality, "n": 1})
        j = call([f"{API}/generations", *auth, "-H", "Content-Type: application/json", "-d", body])
    return base64.b64decode(j["data"][0]["b64_json"]), j.get("usage"), "image/png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("views", nargs="*", type=int)
    ap.add_argument("--backend", default="gemini", choices=["gemini", "openai"])
    ap.add_argument("--model", default=None, help="default: gemini-3-pro-image or gpt-image-1")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high"], help="openai only")
    ap.add_argument("--no-refs", action="store_true")
    a = ap.parse_args()

    model = a.model or ("gemini-3-pro-image" if a.backend == "gemini" else "gpt-image-1")
    lock, views = load_prompts()
    OUT.mkdir(exist_ok=True)
    plan = HERE / "floor-plan.png"
    massing = HERE / "massing.png"
    for n in a.views or sorted(views):
        name, text = views[n]
        stem = f"{n:02d}-{slug(name)}"
        refs = []
        if not a.no_refs:
            refs += [massing, plan]
            if n != 1:
                overview = sorted(p for p in OUT.glob("01-*") if p.suffix in (".png", ".jpg"))
                if overview:
                    refs.append(overview[0])
        geometry = ("The first reference image is an exact 3D massing model of the café with every fixture "
                    "labelled; the second is the dimensioned floor plan it was built from. Keep every object "
                    "exactly where the model puts it, at its size: the island is two parallel counters with an "
                    "open walkway between them, the espresso machine, grinders, juicer and sink on the back "
                    "counter, the pastry case and till on the front counter; the back wall is shelving with the "
                    "menu board centred over a low shelf and a door at the far left, with no counter against "
                    "it; three open chillers fill the left wall under a lightbox sign; open snack shelving "
                    "fills the right wall. ")
        if n == 1 and refs:
            prefix = geometry + ("Render the massing model photorealistically from exactly its camera "
                                 "position; the output must be a photograph-like render, not a diagram. ")
        elif len(refs) == 3:
            prefix = geometry + ("The third reference is the approved overview render of the same café: "
                                 "match its materials, colours and lighting, and render the view described "
                                 "below from inside that exact space. ")
        else:
            prefix = ""
        prompt = prefix + lock + " " + text
        t0 = time.time()
        if a.backend == "gemini":
            img, usage, mime = generate_gemini(model, prompt, size_for(text), refs)
        else:
            img, usage, mime = generate(model, prompt, size_for(text), a.quality, refs)
        path = OUT / (stem + (".jpg" if "jpeg" in mime or "jpg" in mime else ".png"))
        for old in OUT.glob(stem + ".*"):
            if old.suffix in (".png", ".jpg") and old != path:
                old.unlink()
        path.write_bytes(img)
        path.with_suffix(".json").write_text(json.dumps(
            {"view": n, "name": name, "backend": a.backend, "model": model, "quality": a.quality, "size": size_for(text),
             "refs": [r.name for r in refs], "prompt": prompt, "usage": usage}, indent=2), encoding="utf-8")
        print(f"{path.name}  {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
