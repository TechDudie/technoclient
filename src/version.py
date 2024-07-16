import shutil
import zipfile

from src.util import *

META_URL = "https://github.com/PrismLauncher/meta-launcher/archive/refs/heads/master.zip"

def run(version, session):
    log(f"Downloading metadata from {META_URL}{" (REPO@github)".replace("REPO", "/".join(META_URL.split("/")[3:5]) ) if META_URL.startswith("https://github.com") else ""}")

    cache = root() / "cache" / "meta.zip"
    path = root() / "cache" / "meta"
    target = root() / "meta"

    r = session.get(META_URL)
    if r.status_code == 200:
        with open(cache, "wb") as file:
            file.write(r.content)
    else:
        log("Unable to download metadata", "ERROR")
    
    with zipfile.ZipFile(cache) as file:
        file.extractall(path)
    
    try:
        shutil.rmtree(target)
    except FileNotFoundError:
        pass

    shutil.move(path / "meta-launcher-master", target)
    log(f"Extracted contents to {target}")

    log(f"Minecraft metadata downloaded{" (REPO@github)".replace("REPO", "/".join(META_URL.split("/")[3:5]) ) if META_URL.startswith("https://github.com") else ""}")