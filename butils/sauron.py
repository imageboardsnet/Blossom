import time
import json
import os
import requests
from obj.imageboards import imageboardsb

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

status_path = 'data/status.json'

def get_content():
    if os.path.exists(status_path):
        with open(status_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
def save_content(content):
    with open(status_path, 'w') as f:
        json.dump(content, f)

def set_status_time():
    status = {}
    status = get_content()
    status['last_check'] = int(time.time())
    save_content(status)

def get_status_time():
    status = {}
    status = get_content()
    return str(status['last_check'])
    
def get_status_state():
    status = {}
    status = get_content()
    return str(status['state'])

def set_status_state(state):
    status = {}
    status = get_content()
    status['state'] = state
    save_content(status)

def url_builder(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    else:
        return 'https://' + url

def check_imageboard(imageboard):
    url = url_builder(imageboard['url'])
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 403 or response.status_code == 505:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
    
def check_imageboards():
    set_status_state("checking")
    set_status_time()
    imageboards = imageboardsb()
    for imageboard in imageboards:
        check = check_imageboard(imageboard)
        if imageboard['status'] == 'pending':
            pass
        elif check:
            imageboards.set_status(imageboard['id'], 'active')
        elif not check:
            imageboards.set_status(imageboard['id'], 'offline')
    set_status_state("idle")