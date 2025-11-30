from multiprocessing.pool import ThreadPool as Pool
import argparse
import requests
import sys
import threading
import time

okResp = []
wordlistArray = []
counter = 0
lock = threading.Lock()
start_time = time.time()


def printActivePanels():
    print("\n\n---- ACTIVE URLS ----")
    for url in okResp:
        print(url)


def transferWordlist(wordlist):
    with open(wordlist, "r") as wl:
        for line in wl:
            line = line.strip()
            if not line.startswith("#"):
                wordlistArray.append(line)
    return len(wordlistArray)


def format_eta(seconds):
    if seconds < 0:
        seconds = 0
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def searcher(url, item):
    global counter

    path = wordlistArray[item]
    full_url = url + path

    try:
        resp = requests.get(full_url, timeout=5)
        code = resp.status_code
    except:
        code = None

    if code == 200:
        okResp.append(full_url)

    # progress
    with lock:
        counter += 1
        total = len(wordlistArray)

        elapsed = time.time() - start_time
        speed = counter / elapsed if elapsed > 0 else 0
        remaining = (total - counter) / speed if speed > 0 else 0

        sys.stdout.write(
            f"\r{counter}/{total}  "
            f"Speed: {speed:.1f}/s  "
            f"ETA: {format_eta(remaining)}"
        )
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("-w", "--wordlist",
                        default="/usr/share/wordlists/directory-list-2.3.medium.txt")
    parser.add_argument("-t", "--thread", default=50, type=int)
    args = parser.parse_args()

    url = args.url if args.url.endswith("/") else args.url + "/"
    wordlist = args.wordlist
    thread = args.thread

    transferWordlist(wordlist)

    print(f"Total words: {len(wordlistArray)}\n")
    print("Starting scan...\n")

    pool = Pool(thread)

    for item in range(len(wordlistArray)):
        pool.apply_async(searcher, (url, item))

    pool.close()
    pool.join()

    printActivePanels()


if __name__ == "__main__":
    main()
