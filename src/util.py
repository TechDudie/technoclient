import datetime
import pathlib

def root() -> pathlib.Path:
    return pathlib.Path / ".technoclient"

def log(text: str, level="INFO") -> None:
    print(f"[technoclient-core] [{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [{level}] {text}")

    if level == "ERROR":
        log("Terminating")
        exit(1)