import os
import json

users_path = 'data/users.json'

class usersb:

    def __init__(self):
        if os.path.exists(users_path):
            with open(users_path, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            self.users = []

    def save_users(self):
        with open(users_path, 'w') as f:
            json.dump(self.users, f)

    def check_user(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                return user['id']
        return False
    
    def add_user(self, username, password, role, imageboards):
        user = {
            'id': len(self.users) + 1,
            'username': username,
            'password': password,
            'role': role,
            'imageboards': imageboards
        }
        self.users.append(user)
        self.save_users()
    
    def edit_user(self, user_id, updates):
        for user in self.users:
            if user['id'] == user_id:
                for field, value in updates.items():
                    user[field] = value
                self.save_users()
                break

    def remove_user(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                self.users.remove(user)
                self.save_users()

    def __iter__(self):
        return iter(self.users)