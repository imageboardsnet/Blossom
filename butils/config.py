import os
import json
import time

config_path = 'data/config.json'

def get_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
def save_content(file_path, content):
    with open(file_path, 'w') as f:
        json.dump(content, f)

def get_var(var):
    status = {}
    status = get_content(config_path)
    return str(status[var])

def set_date(var):
    status = {}
    status = get_content(config_path)
    status[var] = int(time.time())
    save_content(config_path,status)

def set_var(var,state):
    status = {}
    status = get_content(config_path)
    status[var] = state
    save_content(config_path,status)