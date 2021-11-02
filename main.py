import cfscrape
import threading
import queue
import datetime
import sys

from bs4 import BeautifulSoup

from modules.rand import Rand

useragents = []
proxylist = []


def request_scrape(rand):
    scraper = cfscrape.create_scraper(delay=10)

    rand_filename = rand.generate_filename()

    rand_proxy = Rand.random_proxy(proxylist) if len(proxylist) > 1 else {
        'https': 'socks5h://127.0.0.1:1080'}
    rand_useragent = Rand.random_useragent(useragents) if len(
        useragents) > 1 else 'Discordbot 2.0'

    request_headers = {'user-agent': rand_useragent}

    try:
        r = scraper.get(f'https://prnt.sc/{rand_filename}',
                        proxies=rand_proxy, headers=request_headers, timeout=20.0)
    except:
        print(f'Request failed. | Proxy: {rand_proxy}')
        return

    if (stat_code := r.status_code) != 200:
        print(f'Cannot get to the {r.url} ({stat_code}) | Proxy: {rand_proxy}')
        return

    try:
        soup = BeautifulSoup(r.text, features='html.parser')
        image_id = soup.find(id='screenshot-image')
        image_src = image_id.get('src')

        if image_src.find('https://') == -1:
            print(
                f'Bad file. (deleted or invalid) ({rand_filename}) | Proxy: {rand_proxy}')
        else:
            print(
                f"- Image found -\nRandom name: {rand_filename} | URL: {image_src} | CF RAY: {r.headers['cf-ray']} | Proxy: {rand_proxy}")

            url_log = open('log/urls.log', 'a')
            url_log.write(
                f"[{datetime.datetime.now().ctime()}] - [{rand_filename}] - {image_src}\n")
            url_log.close()
    except:
        print(
            f'Unhandled exception (could be bs4) | Filename: {rand_filename}')
    finally:
        r.close()


jobs = queue.Queue()


def worker():
    while True:
        job = jobs.get()

        # Open a rand for each thread because of json db.
        rand = Rand()
        request_scrape(rand)
        rand.db.close()

        jobs.task_done()


def main():
    if(len(sys.argv) < 4):
        print(
            'Syntax: <threads> <requests> [proxylist] [useragents]')
        return

    try:
        threads = int(sys.argv[1])
        requests = int(sys.argv[2])
    except ValueError as err:
        print(f'Arguments error. ({err})')
        return

    proxylist_file = sys.argv[3]
    useragents_file = sys.argv[4]

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

    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    for i in range(requests):
        jobs.put(i)
    jobs.join()

    print('Done!')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Closing..')
