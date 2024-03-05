import schedule
import time
from endpoints import build_endpoints
from sauron import check_imageboards

def main():
    schedule.every().hour.do(build_endpoints)
    schedule.every().hour.do(check_imageboards)
    while True:
        schedule.run_pending()
        time.sleep(1)