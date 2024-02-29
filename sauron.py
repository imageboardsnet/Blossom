import schedule
import time
import os
import requests
from obj.imageboards import imageboardsb
from utils import check_onlines

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}


def check_imageboards(imageboards):
    for imageboard in imageboards:
        url = imageboard['url']
        status = check_onlines(url)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200 or response.status_code == 403 or response.status_code == 505
                return url, True, "OK"
            else:
                return url, False, f"Error: Status code {response.status_code}"
        except requests.exceptions.RequestException as e:
            return url, False, f"Request Exception: {e}"