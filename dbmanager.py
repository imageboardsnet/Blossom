import os
import json

imageboards_path = 'data/boards/imageboards.json'

def load_imageboards():
    imageboards = {}
    if os.path.exists(imageboards_path):
        with open(imageboards_path, 'r') as f:
            imageboards = json.load(f)
            return imageboards
    else:
        print('No imageboards found, creating new file')

def save_imageboards(imageboards):
    with open(imageboards_path, 'w') as f:
        json.dump(imageboards, f)

def assign_fields(imageboards):
    id_counter = 1
    for imageboard in imageboards:
        imageboard['id'] = id_counter
        id_counter += 1
        imageboard['favicon'] = ""
        imageboard['description'] = ""
        imageboard['activity'] = 0
        imageboard['boards'] = []
        imageboard['created'] = ""
        imageboard['status'] = False
    return imageboards

def ingest_imageboard():
    imageboards = load_imageboards()
    imageboards = assign_fields(imageboards)
    save_imageboards(imageboards)

def edit_imageboard(imageboard_id, field, value):
    imageboards = load_imageboards()
    for imageboard in imageboards:
        if imageboard['id'] == imageboard_id:
            imageboard[field] = value
    save_imageboards(imageboards)

ingest_imageboard()