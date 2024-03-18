import json
import os
import time
from obj.imageboards import imageboardsb

status_path = 'data/endpoints.json'

def get_content():
    if os.path.exists(status_path):
        with open(status_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
def save_content(content):
    with open(status_path, 'w') as f:
        json.dump(content, f)

def set_build_date():
    status = {}
    status = get_content()
    status['build_date'] = int(time.time())
    save_content(status)

def get_build_date():
    status = {}
    status = get_content()
    return str(status['build_date'])

def build_endpoint(legacy=False):
    imageboards = imageboardsb()
    clean_imageboards = []
    for imageboard in imageboards:
        if imageboard['status'] == 'active':
            if legacy:
                modified_imageboard = {key: value for key, value in imageboard.items() if key not in ('id', 'status', 'activity', 'description', 'favicon', 'boards')}
            else:
                modified_imageboard = imageboard.copy()
            clean_imageboards.append(modified_imageboard)
    return clean_imageboards

def build_endpoints():
    set_build_date()
    endpoint = build_endpoint()
    endpoint_legacy = build_endpoint(legacy=True)
    with open('endpoints/imageboards.json', 'w') as f:
        json.dump(endpoint, f)
    with open('endpoints/imageboards_legacy.json', 'w') as f:
        json.dump(endpoint_legacy, f)
