import requests
import dns.resolver
import time
from var.auth import secret_key
from obj.imageboards import imageboardsb

def download_favicon(url, path):
    try:
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
    except:
        pass
    return path

def check_dns_txtrecord(url):
    try:
        answers = dns.resolver.resolve(url, 'TXT')
        return answers
    except:
        return False

def time_elapsed_str(last_check_time):
    time_elapsed = int(time.time()) - int(last_check_time)
    time_elapsed_str = ""
    if time_elapsed < 60:
        time_elapsed_str = f"{time_elapsed} seconds ago"
    elif time_elapsed < 3600:
        minutes = time_elapsed // 60
        time_elapsed_str = f"{minutes} minutes ago"
    else:
        hours = time_elapsed // 3600
        time_elapsed_str = f"{hours} hours ago"
    return time_elapsed_str

def verify_hcaptcha(token):
    """ Verify hCaptcha token. """
    data = {
        'response': token,
        'secret': secret_key
    }
    r = requests.post('https://hcaptcha.com/siteverify', data=data)
    if r.status_code != 200:
        return False
    if r.json().get('success') is None:
        return False
    return r.json().get('success')

def check_claimed_imageboard(user_uuid, ib_id):
    """ Check if user has claimed imageboard. """
    imageboards = imageboardsb()
    imageboard = imageboards.get_imageboard(ib_id)
    if imageboard is None:
        return False
    ib_url = imageboard['url']
    txtrecords = check_dns_txtrecord(ib_url)
    if txtrecords is False:
        return False
    for txtrecord in txtrecords:
        if txtrecord.to_text() == "ibclaim-" + user_uuid:
            return True
    return False

