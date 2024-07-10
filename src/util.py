import datetime
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