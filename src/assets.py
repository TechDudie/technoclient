import hashlib
import json
import multiprocessing
import os

from src.util import *

ASSET_URL = "https://resources.download.minecraft.net"
WIDTH = os.get_terminal_size().columns

def download(data):
    if os.path.exists(data[1]):
        return (2, data)
    
    r = data[3].get(data[0])
    if r.status_code == 200:
        os.makedirs(os.path.dirname(data[1]), exist_ok=True)
        with open(data[1], "wb") as file:
            file.write(r.content)
    else:
        return (1, data)
    return (0, data)

def verify(data):
    try:
        open(data[1], "rb")
    except FileNotFoundError:
        return (2, data)
    
    with open(data[1], "rb") as file:
        return (int(not hashlib.sha1(file.read()).hexdigest() == data[2]), data)

def download_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print(f"Downloading assets    {str(round(j * 100)).rjust(3, ' ')}% [{('/' * int(j * (WIDTH - 29))).ljust(WIDTH - 29, ' ')}]", end="\r")

def verify_callback(status):
    global i, j, delta
    i += 1
    j += delta

    if status[0] != 0:
        download(status[1])
    
    print(f"Verifying assets      {str(round(j * 100)).rjust(3, ' ')}% [{('/' * int(j * (WIDTH - 29))).ljust(WIDTH - 29, ' ')}]", end="\r")

def run(version, session):
    v = version.split("-")[0]
    id = json.loads(open(root() / "meta" / "net.minecraft" / f"{v}.json").read())['assetIndex']['id']
    asset_data = json.loads(open(root() / "assets" / "indexes" / f"{id}.json").read())["objects"]
    data = [(
        f"{ASSET_URL}/{asset['hash'][:2]}/{asset['hash']}",
        root() / "assets" / "objects" / asset['hash'][:2] / asset['hash'],
        asset["hash"],
        session
    ) for asset in asset_data.values()]

    # for reference each asset is formatted as (url, path, hash, session)

    log(f"Downloading {len(data)} assets for Minecraft version {v}")

    multiprocessing.freeze_support()

    global i, j, delta
    delta = 1 / len(data)
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    i = j = 0
    for asset in data:
        pool.apply_async(download, args=(asset, ), callback=download_callback)
    
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    print()

    i = j = 0
    for asset in data:
        pool.apply_async(verify, args=(asset, ), callback=verify_callback)
    
    pool.close()
    pool.join()

    print()

    log(f"Minecraft assets for {v} installed")