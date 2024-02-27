import os
import json

imageboards_path = 'data/boards/imageboards.json'

class imageboardsb:
    def __init__(self):
        if os.path.exists(imageboards_path):
            with open(imageboards_path, 'r', encoding='utf-8') as f:
                self.imageboards = json.load(f)

    def save_imageboards(self):
        with open(imageboards_path, 'w') as f:
            json.dump(self.imageboards, f)

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

    def __iter__(self):
        return iter(self.imageboards)

    def assign_fields(self):
        id_counter = 1
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
        self.imageboards = {k: v for k, v in sorted(imageboard.items())}
        self.save_imageboards()