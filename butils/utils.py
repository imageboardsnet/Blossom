import requests
import dns.resolver
import time
from yarl import URL
import whois
from butils.config import get_var
from obj.imageboards import imageboardsb
import datetime

def check_if_dns_resolves(url):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']
    domain = URL(url).host
    try:
        resolver.resolve(domain)
        return True
    except:
        return False

def query_txt_records(domain):
    txt_records = []
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']
    domain = URL(domain).host
    try:
        answers = resolver.resolve(domain, 'TXT')
        for rdata in answers:
            for txt_string in rdata.strings:
                decoded_string = txt_string.decode('utf-8')
                txt_records.append(decoded_string)
    except:
        return False
    return txt_records

def get_domain_creation_date(domain):
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        return creation_date
    except Exception as e:
        return None
    
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

def timestamp_to_humane(value, format='%d %B %Y'):
    value = int(value)
    return datetime.datetime.utcfromtimestamp(value).strftime(format)

def verify_hcaptcha(token):
    """ Verify hCaptcha token. """
    data = {
        'response': token,
        'secret': get_var('hcaptcha_secret_key')
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
    txtrecords = query_txt_records(ib_url)
    if txtrecords is False:
        return False
    for txtrecord in txtrecords:
        if txtrecord == "ibclaim-" + user_uuid:
            return True
    return False

class ThreadPoolExecutorWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=2)
        return cls._instance

    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)