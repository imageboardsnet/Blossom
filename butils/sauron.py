import requests
from obj.imageboards import imageboardsb
from butils.config import set_date, set_var
from butils.utils import check_if_dns_resolves
from yarl import URL


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def check_imageboard(imageboard):
    url = URL(imageboard['url']).host
    url = f"https://{url}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 403 or response.status_code == 505:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
    
def check_imageboards(thread_event):
    try:
        set_var('sauron_state', 'checking')
        set_date('sauron_last_check')
        imageboardsl = imageboardsb()
        
        for imageboard in imageboardsl:

            if not thread_event.is_set():
                print("Sauron check canceled")
                set_var('sauron_state', 'canceled')
                return
                
            try:
                if not check_if_dns_resolves(imageboard['url']):
                    if imageboard['protocol'] == 'https':
                        imageboardsl.set_status(imageboard['id'], 'offline')
                    continue
                check = check_imageboard(imageboard)
                if imageboard['status'] == 'pending':
                    pass
                elif check:
                    imageboardsl.set_sauron_status(imageboard['id'], 'active')
                elif not check:
                    imageboardsl.set_sauron_status(imageboard['id'], 'offline')
                if not thread_event.is_set():
                    print("Sauron check canceled")
                    set_var('sauron_state', 'canceled')
                    return
                
            except Exception as e:
                print(f"Error checking imageboard {imageboard['id']}: {e}")
                continue
                
        set_var('sauron_state', 'idle')
        
    except Exception as e:
        print(f"Error in check_imageboards: {e}")
        set_var('sauron_state', 'error')
