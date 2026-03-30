import os
from ddgs import DDGS
import time

def download_pest_images():
    # New pest classes with search queries
    pest_queries = {
        'stem_borers': [
            'stem borer caterpillar pest',
            'maize stem borer larva',
            'sugarcane stem borer',
            'busseola fusca stem borer'
        ],
        'mealybugs': [
            'mealybug insect pest',
            'pink mealybug agriculture',
            'cassava mealybug',
            'mealybug close up'
        ],
        'aphid': [
            'aphid insect pest',
            'green aphid plant',
            'black aphid agriculture',
            'aphid colony leaf'
        ]
    }
    
    with DDGS() as ddgs:
        for pest_class, queries in pest_queries.items():
            class_dir = f'dataset_new/{pest_class}'
            os.makedirs(class_dir, exist_ok=True)
            
            print(f"\n📥 Downloading {pest_class}...")
            
            downloaded = 0
            for query in queries:
                try:
                    results = list(ddgs.images(query, max_results=20))
                    
                    for i, result in enumerate(results):
                        try:
                            import requests
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            response = requests.get(result['image'], headers=headers, timeout=10)
                            
                            if response.status_code == 200:
                                ext = result['image'].split('.')[-1].split('?')[0]
                                if ext not in ['jpg', 'jpeg', 'png']:
                                    ext = 'jpg'
                                
                                filepath = f'{class_dir}/{pest_class}_{downloaded}.{ext}'
                                with open(filepath, 'wb') as f:
                                    f.write(response.content)
                                
                                downloaded += 1
                                print(f"  ✅ {downloaded}")
                                time.sleep(0.5)
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"  ❌ Query failed: {e}")
                    continue
            
            print(f"   Total: {downloaded} images")

if __name__ == '__main__':
    download_pest_images()