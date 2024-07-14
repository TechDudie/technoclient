import hashlib
import json
import multiprocessing
import os
import platform
import re
import shutil
import sys
import warnings
import zipfile
warnings.filterwarnings("ignore")
import requests

ARCH = {"X86_64": "x64", "ARM64": "arm64"}["".join([i if i in platform.version() else "" for i in ["X86_64", "ARM64"]])]
WIDTH = os.get_terminal_size().columns

def parse_rule(rule, options) -> bool:
    if rule["action"] == "allow": value = False
    elif rule["action"] == "disallow": value = True

    for os_key, os_value in rule.get("os", {}).items():
        if os_key == "name":
            if os_value == "windows" and platform.system() != 'Windows': return value
            elif os_value == "osx" and platform.system() != 'Darwin': return value
            elif os_value == "linux" and platform.system() != 'Linux': return value
        elif os_key == "arch" and os_value == "x86" and platform.architecture()[0] != "32bit": return value
        elif os_key == "version" and not re.match(os_value, f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}" if platform.system() == "Windows" else platform.uname().release): return value

    return not value

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

def extract(data):
    try: 
        with zipfile.ZipFile(data[0]) as file:
            for f in file.namelist():
                if ARCH not in f: continue
                if len([i for i in re.finditer("\.", f)]) > 1: continue

                if f.endswith(os.sep): continue
                if f.endswith("MF"): continue
                if f.endswith("LIST"): continue
                if f.endswith("class"): continue

                file.extract(f, f"{data[1]}/cache/natives/")
                shutil.move(os.path.join(f"{data[1]}/cache/natives/", f), f"{data[1]}/versions/{data[2]}/natives/{f.split(os.sep)[-1]}")
    except FileNotFoundError: return (1, data[0])
    return (0, data)

def download_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print("\033[1A\x1b[2K")
    print(f"Downloading libraries {str(round(j * 100)).rjust(2, ' ')}% [{('█' * int(j * (WIDTH - 29))).ljust(WIDTH - 30, ' ')}]", end="")

def verify_callback(status):
    global i, j, delta
    i += 1
    j += delta

    if status[0] != 0:
        download(status[1])

    print("\033[1A\x1b[2K")
    print(f"Verifying libraries {str(round(j * 100)).rjust(2, ' ')}% [{('█' * int(j * (WIDTH - 27))).ljust(WIDTH - 28, ' ')}]", end="")

def extract_callback(status):
    global i, j, delta
    i += 1
    j += delta

    print("\033[1A\x1b[2K")
    print(f"Extracting natives {str(round(j * 100)).rjust(2, ' ')}% [{('█' * int(j * (WIDTH - 26))).ljust(WIDTH - 27, ' ')}]", end="")

def run(directory, version, proxy):
    library_data = json.loads(open(f"{directory}/versions/{version}/{version}.json").read())["libraries"]
    
    multiprocessing.freeze_support()

    data = []
    natives = []
    for library in library_data:
        if "rules" in library and (False if any([parse_rule(i, {}) for i in library["rules"]]) else True): continue
        sections = library["name"].split(":")
        data.append((library["downloads"]["artifact"]["url"], f"{directory}/libraries/{'/'.join(sections[0].split('.'))}/{sections[1]}/{sections[2]}/{sections[1]}-{sections[2]}{'-' + sections[3] if 3 < len(sections) else ''}.jar", {"http": f"socks5h://{proxy}", "https": f"socks5h://{proxy}", "socks5": f"socks5h://{proxy}"}, library["downloads"]["artifact"]["sha1"]))
        if "native" in library["name"]: natives.append((f"{directory}/libraries/{'/'.join(sections[0].split('.'))}/{sections[1]}/{sections[2]}/{sections[1]}-{sections[2]}{'-' + sections[3] if 3 < len(sections) else ''}.jar"))

    delta = 1 / len(data)
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    print("")
    i, j = 0, 0
    for asset in data:
        pool.apply_async(download, args=(asset, ), callback=download_callback)
    
    pool.close()
    pool.join()

    print("\n")
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    i, j = 0, 0
    for asset in data:
        pool.apply_async(verify, args=(asset, ), callback=verify_callback)
    
    pool.close()
    pool.join()
    
    os.makedirs(os.path.dirname(f"{directory}/versions/{version}/natives/"), exist_ok=True)
    delta = 1 / len(natives)

    print(natives)

    print("\n")
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    i, j = 0, 0
    for path in natives:
        pool.apply_async(extract, args=((path, directory, version), ), callback=extract_callback)
    
    pool.close()
    pool.join()

    print(f"\n\nMinecraft libraries for {version} installed successfully!")
