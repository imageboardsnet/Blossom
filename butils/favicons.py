from obj.imageboards import imageboardsb
import requests
from butils.config import set_date
import time

def download_favicons():
    set_date('favicon_download_date')
    imageboards = imageboardsb()
    for imageboard in imageboards.imageboards:
        if imageboard['status'] == 'active':
            try:
                response = requests.get('https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=' + imageboard['url'], timeout=10)
                if response.status_code == 200:
                    with open(f'data/favicons/{imageboard["id"]}.ico', 'wb') as f:
                        f.write(response.content)
            except:
                pass