import time
import json
import os
import requests
from obj.imageboards import imageboardsb
import threading

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

def check_imageboard(imageboard):
    url = imageboard['url']
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 403 or response.status_code == 505:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
    
def check_imageboards():
    if get_status_state() == "running":
        return
    imageboardsl = imageboardsb()
    threads = []
    set_status_time()
    set_status_state("running")
    
    for imageboard in imageboardsl:
        thread = threading.Thread(target=check_imageboard, args=(imageboard,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    for imageboard in imageboardsl:
        if imageboard['status'] == "active":
            imageboardsl.set_status(imageboard['id'], "active")
        else:
            imageboardsl.set_status(imageboard['id'], "inactive")

    set_status_state("idle")