import datetime
import hashlib
import os
import pathlib

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