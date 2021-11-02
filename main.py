#!/usr/bin/python3

import cfscrape
import threading
import queue
import datetime
import sys
import time

from bs4 import BeautifulSoup

from modules.rand import Rand
from modules.jobs import ScrapeJob

useragents = []
proxylist = []

jobs_queue = queue.Queue()


def request_scrape(rand_filename, timeout=10.0):
    scraper = cfscrape.create_scraper(delay=10)

    rand_proxy = Rand.random_proxy(proxylist) if len(proxylist) > 1 else {
        'https': 'socks5h://127.0.0.1:1080'}
    rand_useragent = Rand.random_useragent(useragents) if len(
        useragents) > 1 else 'Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0'

    request_headers = {'user-agent': rand_useragent}

    try:
        r = scraper.get(f'https://prnt.sc/{rand_filename}',
                        proxies=rand_proxy, headers=request_headers, timeout=timeout)
    except:
        print(
            f'Request failed. | Filename: {rand_filename} | Proxy: {rand_proxy}')
        return

    if (stat_code := r.status_code) != 200:
        print(
            f'Cannot get to the {r.url} ({stat_code}) | Filename: {rand_filename} | Proxy: {rand_proxy}')
        return

    try:
        soup = BeautifulSoup(r.text, features='html.parser')
        image_id = soup.find(id='screenshot-image')
        image_src = image_id.get('src')

        if image_src.find('https://') == -1:
            print(
                f'Bad file. (deleted or invalid) | Filename: ({rand_filename}) | Proxy: {rand_proxy}')
        else:
            print(
                f"\n- Image found -\nFilename: {rand_filename} | URL: {image_src} | CF RAY: {r.headers['cf-ray']} | Proxy: {rand_proxy}\n")

            url_log = open('log/urls.log', 'a')
            url_log.write(
                f'[{datetime.datetime.now().ctime()}] - [{rand_filename}] - {image_src}\n')
            url_log.close()
    except:
        print(
            f'Unhandled exception (could be bs4) | Filename: {rand_filename} | Proxy: {rand_proxy}')
    finally:
        r.close()


def worker(request_timeout):
    while True:
        job = jobs_queue.get()
        request_scrape(job.random_string, request_timeout)
        jobs_queue.task_done()


def main():
    if(len(sys.argv) < 5):
        print(
            'Syntax: <threads> <requests> <request timeout> [proxylist] [useragents]')
        return

    try:
        threads = int(sys.argv[1])
        requests = int(sys.argv[2])
        request_timeout = float(sys.argv[3])
    except ValueError as err:
        print(f'Invalid arguments. ({err})')
        return

    start_time = time.time()

    proxylist_file = sys.argv[4]
    useragents_file = sys.argv[5]

    try:
        proxies = open(proxylist_file, 'r')

        proxies_content = proxies.read().splitlines()
        for line in proxies_content:
            proxylist.append(line)
    except (IOError, IndexError) as err:
        print(f'Cannot read proxylist. ({err})')
        return

    try:
        ua = open(useragents_file, 'r')

        ua_content = ua.read().splitlines()
        for line in ua_content:
            useragents.append(line)
    except (IOError, IndexError) as err:
        print(f'Cannot read useragents list. ({err})')
        return

    for i in range(threads):
        t = threading.Thread(
            name=f'Scrape_Thread-{i}', target=worker, daemon=True, args=(request_timeout,))
        t.start()

    rand = Rand()

    for i in range(requests):
        rand_string = rand.generate_filename()
        jobs_queue.put(ScrapeJob(rand_string))
    jobs_queue.join()

    end_time = time.time()

    print(
        f'\nElapsed time on {threads} threads and {requests} requests - {str(end_time-start_time)[0:4]} seconds')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Received keyboard interrupt.. Closing the program!')
