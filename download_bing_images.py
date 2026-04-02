#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download pest images using Bing Image Search
"""

import os
import time
import requests
from pathlib import Path

def download_bing_images(query, output_dir, num_images=100):
    """Download images from Bing"""
    print(f"Downloading {num_images} images for: {query}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get existing count
    existing = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
    needed = max(0, num_images - existing)
    
    if needed <= 0:
        print(f"  Already have {existing} images for {query}")
        return existing
    
    # Bing API endpoint (using public API)
    url = "https://www.bing.com/images/async"
    
    downloaded = 0
    offset = 0
    
    try:
        while downloaded < needed and offset < 500:
            params = {
                'q': query,
                'first': offset,
                'count': 35,
                'qft': 'filterui:photo-photo'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            html = response.text
            
            # Extract image URLs from HTML (simple parsing)
            import re
            img_urls = re.findall(r'murl":"([^"]+)"', html)
            
            if not img_urls:
                break
                
            for img_url in img_urls:
                if downloaded >= needed:
                    break
                    
                try:
                    # Download image
                    img_response = requests.get(img_url, timeout=5, stream=True)
                    if img_response.status_code == 200:
                        timestamp = int(time.time())
                        filename = f"{query.replace(' ', '_')}_{timestamp}_{downloaded:04d}.jpg"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            for chunk in img_response.iter_content(1024):
                                f.write(chunk)
                        
                        downloaded += 1
                        print(f"  [{downloaded}/{needed}] Downloaded: {filename}")
                        time.sleep(0.3)
                        
                except Exception as e:
                    continue
                    
            offset += 35
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"  Downloaded {downloaded} new images for {query}")
    return existing + downloaded

def main():
    print("=" * 60)
    print("AGROGUARD - BING IMAGE DOWNLOADER")
    print("=" * 60)
    
    pests = [
        ("armyworm caterpillar", 100),
        ("aphid insect", 100),
        ("mealybug insect", 100),
        ("weevil beetle", 100),
        ("stem borer larva", 100),
    ]
    
    print("\nDownloading pest images from Bing...\n")
    
    for pest_name, target in pests:
        folder_name = pest_name.split()[0].replace('_', '')
        if 'armyworm' in folder_name:
            folder_name = 'armyworm'
        elif 'aphid' in folder_name:
            folder_name = 'aphid'
        elif 'mealybug' in folder_name:
            folder_name = 'mealybugs'
        elif 'weevil' in folder_name:
            folder_name = 'weevil'
        elif 'stem' in folder_name:
            folder_name = 'stem_borers'
            
        output_dir = f"dataset_new/{folder_name}"
        
        print(f"\n--- {folder_name.upper()} ---")
        count = download_bing_images(pest_name, output_dir, target)
        print(f"  Total: {count}")
        
        time.sleep(2)
    
    print("\nComplete! Run: python retrain_with_none.py")

if __name__ == "__main__":
    main()
