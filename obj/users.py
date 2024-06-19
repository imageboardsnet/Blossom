import os
import json
from argon2 import PasswordHasher
import uuid 
import time

users_path = 'data/users.json'

ph = PasswordHasher()

class usersb:

    def __init__(self):
        if os.path.exists(users_path):
            with open(users_path, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            self.users = []
            self.save_users()

    def save_users(self):
        with open(users_path, 'w') as f:
            json.dump(self.users, f)

    def check_user(self, username, password):
        for user in self.users:
            if user['username'] == username and ph.verify(user['password'], password):
                if ph.check_needs_rehash(user['password']):
                    user['password'] = ph.hash(password)
                    self.save_users()
                return user['id']
        return False
    
    def get_user(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user
        return False
    
    def get_username(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user['username']
        return False
    
    def add_user(self, username, password, role, imageboards, claim):
        password = ph.hash(password)
        useruuid = str(uuid.uuid4())
        creation_date = int(time.time())
        user = {
            'id': len(self.users) + 1,
            'username': username,
            'password': password,
            'role': role,
            'imageboards': imageboards,
            'claim': claim,
            'uuid': useruuid,
            'creation_date' : creation_date
        }
        self.users.append(user)
        self.save_users()
    
    def set_password(self, user_id, password):
        for user in self.users:
            if user['id'] == user_id:
                user['password'] = ph.hash(password)
                self.save_users()
                break

    def remove_user(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                self.users.remove(user)
                self.save_users()

    def add_imageboard(self, user_id, imageboard_id):
        for user in self.users:
            if user['id'] == int(user_id):
                user['imageboards'].append(imageboard_id)
                self.save_users()
                break
    
    def add_claim(self, user_id, imageboard_id):
        for user in self.users:
            if user['id'] == int(user_id):
                user['claim'].append(imageboard_id)
                self.save_users()
                break

    def remove_claim(self, user_id, imageboard_id):
        for user in self.users:
            if user['id'] == int(user_id):
                user['claim'].remove(imageboard_id)
                self.save_users()
                break

    def __iter__(self):
        return iter(self.users)