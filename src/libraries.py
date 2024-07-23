import hashlib
import json
import multiprocessing
import os
import platform
import re
import shutil
import zipfile

from src.util import *

ARCH = {"x86_64": "x64", "X86_64": "x64", "AMD64": "x64", "ARM64": "aarch64"}["".join([i if i in platform.uname()[4] else "" for i in ["x86_64", "X86_64", "AMD64", "ARM64"]])]
WIDTH = os.get_terminal_size().columns
NATIVE_ID = {"Windows": "windows", "Darwin": "osx", "Linux": "linux"}[platform.system()]

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

def extract(data):
    with zipfile.ZipFile(data) as file:
        print(f"{data}: {file.namelist()}")
        for f in file.namelist():

            if f.endswith(os.sep): continue
            if f.endswith("MF"): continue
            if f.endswith("LIST"): continue
            if f.endswith("class"): continue

            path = root() / "version" / v / "natives" / f.split(os.sep)[-1]
            os.makedirs(os.path.dirname(path), exist_ok=True)
            file.extract(f, path)
    
    return (0, data)

def download_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print(f"Downloading libraries {str(round(j * 100)).rjust(3, ' ')}% [{('/' * int(j * (WIDTH - 29))).ljust(WIDTH - 29, ' ')}]", end="\r")

def verify_callback(status):
    global i, j, delta
    i += 1
    j += delta

    if status[0] != 0:
        download(status[1])
    
    print(f"Verifying libraries   {str(round(j * 100)).rjust(3, ' ')}% [{('/' * int(j * (WIDTH - 29))).ljust(WIDTH - 29, ' ')}]", end="\r")

def extract_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print(f"Extracting natives    {str(round(j * 100)).rjust(3, ' ')}% [{('/' * int(j * (WIDTH - 29))).ljust(WIDTH - 29, ' ')}]", end="\r")

def run(version, session):
    global v, i, j, delta
    v = version.split("-")[0]
    library_data = json.load(open(root() / "meta" / "com.mojang" / f"{v}.json"))["libraries"]

    data = []
    natives = []
    for library in library_data:
        if "rules" in library and False in [parse_rule(i) for i in library["rules"]]: continue
        sections = library["name"].split(":")

        if "artifact" in library["downloads"]:
            data.append((
                library["downloads"]["artifact"]["url"],
                os.path.join(root() / "libraries", convert_path(sections)),
                library["downloads"]["artifact"]["sha1"],
                session
            ))
        
        if "classifiers" in library["downloads"]:
            id = library["natives"][NATIVE_ID].replace("${arch}", ARCH[-2:])
            data.append((
                library["downloads"]["classifiers"][id]["url"],
                os.path.join(root() / "libraries", convert_path(sections)),
                library["downloads"]["classifiers"][id]["sha1"],
                session
            ))
        
        if "natives" in library:
            natives.append((
                os.path.join(root() / "libraries", convert_path(sections))
            ))

    delta = 1 / len(data)

    # for reference each asset is formatted as (url, path, hash, session)

    log(f"Downloading {len(data)} libraries for Minecraft version {v}")

    multiprocessing.freeze_support()
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    i, j = 0, 0
    for asset in data:
        pool.apply_async(download, args=(asset, ), callback=download_callback)
    
    pool.close()
    pool.join()

    print()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    i, j = 0, 0
    for asset in data:
        pool.apply_async(verify, args=(asset, ), callback=verify_callback)
    
    pool.close()
    pool.join()

    print()
    
    os.makedirs(os.path.dirname(root() / "version" / v / "natives"), exist_ok=True)
    try:
        delta = 1 / len(natives)

        pool = multiprocessing.Pool(multiprocessing.cpu_count())

        i, j = 0, 0
        for native in natives:
            pool.apply_async(extract, args=(native, ), callback=extract_callback)
        
        pool.close()
        pool.join()

        print()
    except ZeroDivisionError:
        log(f"No natives to extract for {v}", "WARN")

    log(f"Minecraft libraries for {v} installed")
