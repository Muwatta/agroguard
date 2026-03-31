import os
import csv
import argparse
from ddgs import DDGS
import time


def _download_url_to_class(class_dir, base_name, url, idx):
    import requests
    headers = {'User-Agent': 'Mozilla/5.0'}

    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"    ⚠️ Attempt {attempt}: {url} -> {response.status_code} {response.reason}")
                time.sleep(1)
                continue

            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"    ⚠️ Attempt {attempt}: content-type not image: {content_type}")
                return False

            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png']:
                ext = 'jpg'

            filepath = os.path.join(class_dir, f"{base_name}_{idx}.{ext}")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True

        except Exception as e:
            print(f"    ⚠️ Attempt {attempt}: error downloading {url}: {e}")
            time.sleep(2)

    return False


def download_pest_images(url_csv=None, max_results=60):
    pest_queries = {
        'stem_borers': [
            'stem borer caterpillar pest',
            'maize stem borer larva',
            'sugarcane stem borer',
            'busseola fusca stem borer',
            'stem borer damage maize',
            'borer pest in stems'
        ],
        'mealybugs': [
            'mealybug insect pest',
            'pink mealybug agriculture',
            'cassava mealybug',
            'mealybug close up',
            'mealybug infestation plant',
            'pineapple mealybug'
        ],
        'aphid': [
            'aphid insect pest',
            'green aphid plant',
            'black aphid agriculture',
            'aphid colony leaf',
            'aphid infestation on crops',
            'aphid eggs on leaf'
        ]
    }

    if url_csv:
        if not os.path.exists(url_csv):
            print(f"URL CSV file not found: {url_csv}")
            return

        tally = {}
        with open(url_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pest_class = row.get('class') or row.get('pest')
                url = row.get('url')
                if not pest_class or not url:
                    continue

                pest_class = pest_class.strip()
                class_dir = f'dataset_new/{pest_class}'
                os.makedirs(class_dir, exist_ok=True)
                tally.setdefault(pest_class, 0)

                idx = tally[pest_class]
                success = False
                try:
                    success = _download_url_to_class(class_dir, pest_class, url, idx)
                except Exception as e:
                    print(f"  ❌ Failed to download {url} for {pest_class}: {e}")

                if success:
                    tally[pest_class] += 1
                    print(f"  ✅ {pest_class} {tally[pest_class]}")

        for c, n in tally.items():
            print(f"   Total downloaded for {c}: {n} images")

        return

    with DDGS() as ddgs:
        for pest_class, queries in pest_queries.items():
            class_dir = f'dataset_new/{pest_class}'
            os.makedirs(class_dir, exist_ok=True)

            print(f"\n📥 Downloading {pest_class}...")
            downloaded = 0

            for query in queries:
                try:
                    results = list(ddgs.images(query, max_results=max_results))
                    for _ in results:
                        try:
                            url = _['image']
                            if not url:
                                continue

                            success = _download_url_to_class(class_dir, pest_class, url, downloaded)
                            if success:
                                downloaded += 1
                                print(f"  ✅ {downloaded}")
                                time.sleep(0.3)
                        except Exception:
                            continue

                except Exception as e:
                    print(f"  ❌ Query failed: {e}")
                    continue

            print(f"   Total: {downloaded} images")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download pest images into dataset_new')
    parser.add_argument('--csv', help='CSV file with class,url rows')
    parser.add_argument('--max-results', type=int, default=60, help='Max results per query for DDGS mode')
    args = parser.parse_args()

    download_pest_images(url_csv=args.csv, max_results=args.max_results)
