import json
from obj.imageboards import imageboardsb
from butils.config import set_date

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
    set_date('endpoint_build_date')
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