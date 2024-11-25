import json
import os
import time

def get_content(path):
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = json.load(f)
                return content
        else:
            default_config = {
                "app_secret_key": "your_secret_key_here",
                "hcaptcha_sitekey": "10000000-ffff-ffff-ffff-000000000001",
                "hcaptcha_secret": "0x0000000000000000000000000000000000000000",
                "sauron_state": "idle",
                "sauron_last_check": 0,
                "favicon_download_date": 0,
                "endpoint_build_date": 0
            }
            with open(path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    except json.JSONDecodeError as e:
        print(f"Error reading config: {e}")
        return None

def get_var(var):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/config.json')
    try:
        status = get_content(config_path)
        return status.get(var, None)
    except Exception as e:
        print(f"Error reading config: {e}")
        return None

def set_var(var, value):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/config.json')
    try:
        config = get_content(config_path)
        config[var] = value
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error writing config: {e}")

def set_date(var):
    set_var(var, int(time.time()))