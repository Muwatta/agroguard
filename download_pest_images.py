#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automatically download pest images from the internet using DuckDuckGo and Bing
"""

import os
import time
import requests
from pathlib import Path
import urllib.parse

def download_duckduckgo_images(query, output_dir, num_images=100):
    """Download images from DuckDuckGo"""
    print(f"Downloading {num_images} images for: {query}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get existing count
    existing = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
    needed = max(0, num_images - existing)
    
    if needed <= 0:
        print(f"  Already have {existing} images for {query}")
        return existing
    
    # DuckDuckGo API endpoint
    url = "https://duckduckgo.com/i.js"
    
    downloaded = 0
    page = 0
    
    try:
        while downloaded < needed:
            params = {
                'q': query,
                'o': 'json',
                'p': page,
                'f': ',,,'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'results' not in data or not data['results']:
                break
                
            for result in data['results']:
                if downloaded >= needed:
                    break
                    
                img_url = result.get('image')
                if not img_url:
                    continue
                    
                try:
                    # Download image
                    img_response = requests.get(img_url, timeout=5, stream=True)
                    if img_response.status_code == 200:
                        timestamp = int(time.time())
                        filename = f"{query}_{timestamp}_{downloaded:04d}.jpg"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            for chunk in img_response.iter_content(1024):
                                f.write(chunk)
                        
                        downloaded += 1
                        print(f"  [{downloaded}/{needed}] Downloaded: {filename}")
                        time.sleep(0.5)  # Be polite to the server
                        
                except Exception as e:
                    print(f"  Error downloading: {e}")
                    continue
                    
            page += 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"  Downloaded {downloaded} new images for {query}")
    return existing + downloaded

def main():
    print("=" * 60)
    print("AGROGUARD - AUTOMATIC PEST IMAGE DOWNLOADER")
    print("=" * 60)
    
    # Pests to download
    pests = [
        ("armyworm", 100),
        ("aphid", 100),
        ("mealybug", 100),
        ("weevil", 100),
        ("stem borer", 100),
    ]
    
    print("\nThis will download pest images from the internet")
    print("Images will be saved to dataset_new/[pest_name]/")
    print("Existing images will be preserved\n")
    
    for pest_name, target in pests:
        # Create folder name (remove spaces)
        folder_name = pest_name.replace(' ', '_')
        if folder_name == 'mealybug':
            folder_name = 'mealybugs'
        elif folder_name == 'stem_borer':
            folder_name = 'stem_borers'
            
        output_dir = f"dataset_new/{folder_name}"
        
        print(f"\n--- Processing {pest_name.upper()} ---")
        count = download_duckduckgo_images(pest_name, output_dir, target)
        print(f"  Total {folder_name} images: {count}")
        
        # Wait between downloads
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    
    # Show final counts
    print("\nFinal dataset sizes:")
    for pest in ['aphid', 'armyworm', 'mealybugs', 'none', 'stem_borers', 'weevil']:
        folder = f"dataset_new/{pest}"
        if os.path.exists(folder):
            count = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
            print(f"  {pest}: {count} images")
    
    print("\nNow run: python retrain_with_none.py")

if __name__ == "__main__":
    # Install requests if not available
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        os.system("pip install requests")
        import requests
    
    main()
