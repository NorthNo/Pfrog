from multiprocessing.pool import ThreadPool as Pool
import argparse
import requests

okResp = []
wordlistArray = []


def printActivePanels():
  print("---- ACTIVE URLS ----")
  for url in okResp:
    print(url)

def transferWordlist(wordlist):
  with open(wordlist, "r") as wl:
    for line in wl:
      line = line.strip()
      
      if not line.startswith("#"):
        wordlistArray.append(line)

  return len(wordlistArray)

def searcher(url, item):
  line = wordlistArray[item]
  req = requests.get(url + line).status_code
    
  if req != 200:
    print("[{}{}]".format(url, line), "=", "\x1b[34m[STATUS_CODE : {}]\x1b[0m".format(req))
  else:
    print("[{}{}]".format(url, line), "=", "\x1b[31;43;4m[STATUS_CODE : {}]\x1b[0m".format(req))
    okResp.append(f"[{url}{line}] = [STATUS_CODE : {req}]")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--url', required=True, help="write a url")
  parser.add_argument('-w', '--wordlist', required=False, default="/usr/share/wordlists/directory-list-2.3.medium.txt", help="enter wordlist directory")
  parser.add_argument('-t', '--thread', required=False, default=10, type=(int), help="Write thread count")
  args = vars(parser.parse_args())
  url = args["url"]
  wordlist = args["wordlist"]
  thread = args["thread"]

  transferWordlist(wordlist)

  pool = Pool(thread)

  for item in range(len(wordlistArray)):
    pool.apply_async(searcher, (url, item,))

  pool.close()
  pool.join()

  printActivePanels()

if __name__ == "__main__":
  main()