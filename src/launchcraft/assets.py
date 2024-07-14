import hashlib
import json
import multiprocessing
import os
import warnings
warnings.filterwarnings("ignore")
import requests

ASSET_URL = "https://resources.download.minecraft.net"
WIDTH = os.get_terminal_size().columns

def download(data):
    if os.path.exists(data[1]): return (2, data)
    
    r = requests.get(data[0], proxies=data[2])
    if r.status_code == 200:
        os.makedirs(os.path.dirname(data[1]), exist_ok=True)
        with open(data[1], "wb") as file: file.write(r.content)
    else: return (1, data)
    return (0, data)

def verify(data):
    try: open(data[1], "rb")
    except FileNotFoundError: return (2, data)
    
    with open(data[1], "rb") as file: return (int(not hashlib.sha1(file.read()).hexdigest() == data[3]), data)

def download_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print("\033[1A\x1b[2K")
    print(f"Downloading assets {str(round(j * 100)).rjust(2, ' ')}% [{('█' * int(j * (WIDTH - 26))).ljust(WIDTH - 27, ' ')}]", end="")

def verify_callback(status):
    global i, j, delta
    i += 1
    j += delta

    if status[0] != 0:
        download(status[1])

    print("\033[1A\x1b[2K")
    print(f"Verifying assets {str(round(j * 100)).rjust(2, ' ')}% [{('█' * int(j * (WIDTH - 24))).ljust(WIDTH - 25, ' ')}]", end="")
    

def run(directory, version, proxy):
    asset_data = json.loads(open(f"{directory}/assets/indexes/{json.loads(open(f'{directory}/versions/{version}/{version}.json').read())['assetIndex']['id']}.json").read())["objects"]

    multiprocessing.freeze_support()

    data = [(f"{ASSET_URL}/{asset['hash'][:2]}/{asset['hash']}", f"{directory}/assets/objects/{asset['hash'][:2]}/{asset['hash']}", {"http": f"socks5h://{proxy}", "https": f"socks5h://{proxy}", "socks5": f"socks5h://{proxy}"} if proxy else None, asset["hash"]) for asset in asset_data.values()]
    delta = 1 / len(data)
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    print("")
    i, j = 0, 0
    for asset in data:
        pool.apply_async(download, args=(asset, ), callback=download_callback)
    
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    print("\n")
    i, j = 0, 0
    for asset in data:
        pool.apply_async(verify, args=(asset, ), callback=verify_callback)
    
    pool.close()
    pool.join()

    print(f"\n\nMinecraft assets for {version} installed successfully!")
