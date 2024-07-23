import datetime
import hashlib
import os
import pathlib
import platform
import re
import sys

NAMESAPCE = "technoclient-core"

def default() -> bool:
    try:
        os.chdir(root())
        return False
    except FileNotFoundError:
        os.mkdir(root())
        return True

def root() -> pathlib.Path:
    return pathlib.Path.home() / ".technoclient"

def log(text: str, level="INFO") -> None:
    print(f"[{NAMESAPCE}] [{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [{level}] {text}")

    if level == "ERROR":
        log("Terminating")
        exit(1)

def download(session, url, path, sha1=None, quiet=False) -> int:
    if pathlib.Path(path).exists():
        if sha1:
            with open(path, "rb") as file:
                if hashlib.sha1(file.read()).hexdigest() == sha1:
                    log(f"{path} present with correct checksum, skipping")
                    return 0
                else:
                    log(f"{path} present with incorrect checksum, redownloading")
    
    if not quiet:
        log(f"Downloading {url} to {path}" + (f" (sha1: {sha1})" if sha1 else ""))
    r = session.get(url)
    if r.status_code == 200:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file:
            file.write(r.content)
    else:
        log(f"Failed to download {url} to {path}", "ERROR")
        return 2
    
    if sha1:
        with open(path, "rb") as file:
            if not hashlib.sha1(file.read()).hexdigest() == sha1:
                log(f"SHA1 hash of downloaded file {path} does not match {url}", "ERROR")
                return 1
            return 0
    
    return 0

def convert_path(sections) -> str:
    # man who invented this
    # TODO: make it use pathlib.Path() through root() sometime or this will ABSOLUTELY cause issues later

    return f"{'/'.join(sections[0].split('.'))}/{sections[1]}/{sections[2]}/{sections[1]}-{sections[2]}{'-' + sections[3] if 3 < len(sections) else ''}.jar"

def parse_rule(rule) -> bool:
    if rule["action"] == "allow":
        value = False
    elif rule["action"] == "disallow":
        value = True
    
    for k, v in rule.get("os", {}).items():
        if k == "name":
            match v:
                case "windows":
                    return value if platform.system() != 'Windows' else not value
                
                case "osx":
                    return value if platform.system() != 'Darwin' else not value
                
                case "linux":
                    return value if platform.system() != 'Linux' else not value
        
        elif k == "arch" and v == "x86" and platform.architecture()[0] != "32bit":
            return value
        elif k == "version" and not re.match(v, f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}" if platform.system() == "Windows" else platform.uname().release):
            return value
    
    return not value