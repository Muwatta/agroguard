"""
AgroGuard Image Downloader (Stable Version)
Uses duckduckgo_search instead of manual scraping.

Usage:
    pip install duckduckgo-search
    python download_images.py
"""

import time
import random
import requests
from pathlib import Path
from duckduckgo_search import DDGS

# ================= CONFIG ================= #

PESTS = {
    "aphid": [
        "aphid insect crop pest",
        "green aphid plant pest",
        "aphid colony leaves pest",
        "black aphid crop damage",
        "aphid infestation agriculture",
    ],
    "mealybugs": [
        "mealybug insect plant pest",
        "mealybug infestation crop",
        "cottony mealybug pest",
        "mealybug on leaves",
        "mealybug agriculture pest close up",
    ],
}

TARGET = 80
OUTPUT_BASE = "dataset_new"

BLOCKED_DOMAINS = [
    "dpi.nsw.gov.au",
    "tandfonline.com",
    "mindenpictures.com",
    "agritech.tnau.ac.in",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ========================================= #


def ddg_image_urls(query: str, max_results: int = 100) -> list[str]:
    """Fetch image URLs using duckduckgo_search (stable)."""
    urls = []

    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=max_results)

            for r in results:
                url = r.get("image")
                if not url:
                    continue

                if any(domain in url for domain in BLOCKED_DOMAINS):
                    continue

                urls.append(url)

    except Exception as e:
        print(f"❌ Search error for '{query}': {e}")

    return urls


def download_image(url: str, dest: Path, idx: int) -> bool:
    """Download a single image safely."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, stream=True)

        if r.status_code != 200:
            return False

        ct = r.headers.get("content-type", "").lower()

        # Accept ANY image type (more flexible)
        if "image" not in ct:
            return False

        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"

        fname = dest / f"img_{idx:04d}{ext}"

        size = 0
        with open(fname, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                size += len(chunk)

        # Remove tiny/broken images
        if size < 5000:
            fname.unlink(missing_ok=True)
            return False

        return True

    except Exception:
        return False


def download_pest(name: str, queries: list[str]):
    dest = Path(OUTPUT_BASE) / name
    dest.mkdir(parents=True, exist_ok=True)

    existing = len(list(dest.glob("*.*")))
    print(f"\n📥 Downloading {name}... (existing: {existing})")

    urls_seen = set()
    all_urls = []

    # 🔍 Gather URLs
    for q in queries:
        print(f"   🔎 Searching: {q}")
        new_urls = ddg_image_urls(q, max_results=100)

        for url in new_urls:
            if url not in urls_seen:
                urls_seen.add(url)
                all_urls.append(url)

        time.sleep(random.uniform(1, 2))

    print(f"   Found {len(all_urls)} candidate URLs")

    # ⬇️ Download images
    idx = existing
    success = 0

    for url in all_urls:
        if existing + success >= TARGET:
            break

        if download_image(url, dest, idx):
            success += 1
            idx += 1
            print(f"  ✅ {existing + success}")
        else:
            print(f"  ⚠️ Failed")

        time.sleep(random.uniform(0.3, 0.8))

    print(f"   ✅ Total {name}: {existing + success} images")


def main():
    for pest, queries in PESTS.items():
        download_pest(pest, queries)

    print("\n🎉 Done.")


if __name__ == "__main__":
    main()