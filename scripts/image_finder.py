from .text_generator import generate_search_query_v1
import httpx
import yaml
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

google_search_api_key = config['google-search-api-key']
google_search_engine_id = config['google-search-engine-id']

def google_search(full_text, num=1):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    
    image_urls = []

    search_queries = generate_search_query_v1(full_text).split("\n")

    for search_query in search_queries:
        try:
            if search_query == '':
                continue
            
            params = {
                'key': google_search_api_key,
                'cx': google_search_engine_id,
                'q': search_query,
                'searchType': 'image',
                'num': num
            }
    
            response = httpx.get(base_url, params=params)
            response.raise_for_status()
    
            data = response.json()
    
            image_url = [item["link"] for item in data.get("items", [])][0]
    
            image_urls.append(image_url)
        except Exception as e:
            print(e)
    return image_urls


def download_images(image_urls, folder="static/temp/fetched_images"):
    os.makedirs(folder, exist_ok=True)
    
    for i, url in enumerate(image_urls, 1):
        try:
            response = httpx.get(url)
            response.raise_for_status()
            
            ext = os.path.splitext(url)[1].split("?")[0]
            if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif"]:
                ext = ".jpg"
            
            file_path = os.path.join(folder, f"image_{i}{ext}")
            
            with open(file_path, "wb") as f:
                f.write(response.content)
                    
        except Exception as e:
            print(f"Failed to download {url}: {e}")
