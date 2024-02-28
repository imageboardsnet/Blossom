import requests
import dns.resolver

def check_onlines(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False
    

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
   