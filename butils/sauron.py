import requests
from obj.imageboards import imageboardsb
from butils.config import set_date, set_var
from butils.utils import clean_url

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def check_imageboard(imageboard):
    url = clean_url(imageboard['url'])
    url = f"https://{url}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 403 or response.status_code == 505:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
    
def check_imageboards():
    set_var('sauron_state','running')
    set_date('sauron_last_check')
    imageboards = imageboardsb()
    for imageboard in imageboards:
        check = check_imageboard(imageboard)
        if imageboard['status'] == 'pending':
            pass
        elif check:
            imageboards.set_sauron_status(imageboard['id'], 'active')
        elif not check:
            imageboards.set_sauron_status(imageboard['id'], 'offline')
    set_var('sauron_state','idle')