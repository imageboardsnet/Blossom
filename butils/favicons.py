from obj.imageboards import imageboardsb
import requests
from butils.config import set_date
import os

def download_favicon(imageboard):
    try:
        response = requests.get('https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=' + imageboard['url'], timeout=10)
        if response.status_code == 200:
            with open(f'data/favicons/{imageboard["id"]}.ico', 'wb') as f:
                f.write(response.content)
    except:
        pass

def download_favicons(onlynew):
    set_date('favicon_download_date')
    imageboards = imageboardsb()
    for imageboard in imageboards.imageboards:
        if imageboard['status'] == 'active':
            if onlynew == True:
                if not os.path.exists(f'data/favicons/{imageboard["id"]}.ico'):
                    download_favicon(imageboard)
            elif onlynew == False:
                download_favicon(imageboard)