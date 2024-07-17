from obj.imageboards import imageboardsb
import requests
from butils.utils import get_content, save_content
import time

status_path = 'data/favicons.json'

def favicon_set_build_date():
    status = {}
    status = get_content(status_path)
    status['download_date'] = int(time.time())
    save_content(status_path,status)

def favicon_get_build_date():
    status = {}
    status = get_content(status_path)
    return str(status['download_date'])

def download_favicons():
    favicon_set_build_date()
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