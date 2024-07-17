import json
import os
import time
from obj.imageboards import imageboardsb
from butils.utils import get_content, save_content

status_path = 'data/endpoints.json'

def set_build_date():
    status = {}
    status = get_content(status_path)
    status['build_date'] = int(time.time())
    save_content(status_path,status)

def get_build_date():
    status = {}
    status = get_content(status_path)
    return str(status['build_date'])

def build_endpoint(legacy=False):
    imageboards = imageboardsb()
    clean_imageboards = []
    for imageboard in imageboards:
        if imageboard['status'] == 'active':
            if legacy:
                modified_imageboard = {key: value for key, value in imageboard.items() if key not in ('id', 'status', 'description', 'favicon', 'boards')}
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

def get_endpoints(legacy=False):
    if legacy:
        with open('endpoints/imageboards_legacy.json', 'r') as f:
            return json.load(f)
    else:
        with open('endpoints/imageboards.json', 'r') as f:
            return json.load(f)