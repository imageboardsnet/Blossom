import os
import json
import requests

imageboards_path = 'data/imageboards.json'

imageboards_endpoint_old = 'https://imageboardsnet.github.io/imageboards.json/imageboards.json'

class imageboardsb:
    def __init__(self):
        if os.path.exists(imageboards_path):
            with open(imageboards_path, 'r', encoding='utf-8') as f:
                self.imageboards = json.load(f)

    def get_last_id(self):
        print (self.imageboards)
        if self.imageboards == []:
            return 0
        return max([imageboard['id'] for imageboard in self.imageboards])

    def save_imageboards(self):
        with open(imageboards_path, 'w') as f:
            json.dump(self.imageboards, f)

    def add_imageboard(self, imageboard):
        new_id = self.get_last_id() + 1
        imageboard['id'] = new_id
        self.imageboards.append(imageboard)
        self.save_imageboards()

    def update_imageboard(self, imageboard_id, updates):
        for imageboard in self.imageboards:
            if imageboard['id'] == imageboard_id:
                for field, value in updates.items():
                    imageboard[field] = value
                self.save_imageboards()
                break
                
    def get_imageboard(self, imageboard_id):
        for imageboard in self.imageboards:
            if imageboard['id'] == imageboard_id:
                return imageboard
            
    def delete_imageboard(self, imageboard_id):
        for imageboard in self.imageboards:
            if imageboard['id'] == imageboard_id:
                self.imageboards.remove(imageboard)
                self.save_imageboards()

    def set_status(self, imageboard_id, status):
        for imageboard in self.imageboards:
            if imageboard['id'] == imageboard_id:
                imageboard['status'] = status
                self.save_imageboards()
                break
                
    def __iter__(self):
        return iter(self.imageboards)
    
    def __len__(self):
        return len(self.imageboards)

    def assign_fields(self):
        self.imageboards = requests.get(imageboards_endpoint_old).json()
        id_counter = 0
        for imageboard in self.imageboards:
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
        self.save_imageboards()