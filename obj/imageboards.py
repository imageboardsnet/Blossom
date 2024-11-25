import os
import json
import requests
from yarl import URL

imageboards_path = 'data/imageboards.json'

class imageboardsb:
    def __init__(self):
        if os.path.exists(imageboards_path):
            with open(imageboards_path, 'r', encoding='utf-8') as f:
                self.imageboards = json.load(f)

    def get_last_id(self):
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

    def set_sauron_status(self, imageboard_id, status):
        for imageboard in self.imageboards:
            if imageboard['id'] == imageboard_id:
                imageboard['sauron_status'] = status
                self.save_imageboards()
                break
                
    def check_if_duplicate(self, imageboard):
        for ib in self.imageboards:
            try:
                ib_url = URL(ib['url'])
                new_url = URL(imageboard['url'])
                
                if not ib_url.host or not new_url.host:
                    continue
                    
                ib_host_parts = ib_url.host.split('.')
                new_host_parts = new_url.host.split('.')
                
                ib_domain = '.'.join(ib_host_parts[-2:] if len(ib_host_parts) > 2 else ib_host_parts)
                new_domain = '.'.join(new_host_parts[-2:] if len(new_host_parts) > 2 else new_host_parts)
                
                if ib_domain == new_domain:
                    return True
            except (KeyError, AttributeError):
                continue
                
        return False

    def __iter__(self):
        return iter(self.imageboards)
    
    def __len__(self):
        return len(self.imageboards)

    def add_protocol(self):
        for ib in self.imageboards:
            ib['protocol'] = 'https'
        self.save_imageboards()

