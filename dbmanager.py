import os
import json

imageboards_path = 'data/boards/imageboards.json'

def load_imageboards():
    imageboards = {}
    if os.path.exists(imageboards_path):
        with open(imageboards_path, 'r', encoding='utf-8') as f:
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
        imageboard['status'] = "offline"
        if 'mirrors' not in imageboard:
            imageboard['mirrors'] = []
        if 'language' not in imageboard:
            imageboard['language'] = ""
        if 'software' not in imageboard:
            imageboard['software'] = ""
    imageboard = {k: v for k, v in sorted(imageboard.items())}
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

def get_imageboard(imageboard_id):
    imageboards = load_imageboards()
    for imageboard in imageboards:
        if imageboard['id'] == imageboard_id:
            return imageboard
        
def delete_imageboard(imageboard_id):
    imageboards = load_imageboards()
    for imageboard in imageboards:
        if imageboard['id'] == imageboard_id:
            imageboards.remove(imageboard)
    save_imageboards(imageboards)

def load_user_database():
    with open("data/users.json", "r") as file:
        users = json.load(file)
    return users

def check_user(users, username, password):
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user['id']

def edit_user(user_id, field, value):
    users = load_user_database()
    for user in users:
        if user['id'] == user_id:
            user[field] = value
    with open("data/users.json", "w") as file:
        json.dump(users, file)

def remove_user(user_id):
    users = load_user_database()
    for user in users:
        if user['id'] == user_id:
            users.remove(user)
    with open("data/users.json", "w") as file:
        json.dump(users, file)