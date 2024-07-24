import json
import os
import shutil
import time
import zipfile

from src.util import *

META_URL = "https://github.com/PrismLauncher/meta-launcher/archive/refs/heads/master.zip"
MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

def run(version, session):
    v = version.split("-")[0]

    log(f"Downloading metadata{" from REPO (https://github.com)".replace("REPO", "/".join(META_URL.split("/")[3:5]) ) if META_URL.startswith("https://github.com") else ""}")

    cache = root() / "cache" / "meta.zip"
    path = root() / "cache" / "meta"
    target = root() / "meta"

    if not os.path.exists(cache) or (time.time() - os.path.getmtime(cache)) < 600:
        r = session.get(META_URL)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(cache), exist_ok=True)
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
    else:
        log("Recent metadata found, skipping download")
    
    log("Downloading game manifest")
    path = root() / "meta" / "manifest.json"
    if download(session, MANIFEST_URL, path, quiet=True) != 0:
        log("Failed to download game manifest", "ERROR")
    
    log("Downloading version data")
    data = json.load(open(path))["versions"]
    path = root() / "meta" / "com.mojang" / f"{v}.json"
    for i in data:
        if i["id"] == v:
            if download(session, i["url"], path, quiet=True) != 0:
                log(f"Failed to download version data for {v}", "ERROR")
    
    log("Downloading modern version data") # TODO: because used for arguments, just hardcode the json
    path = root() / "meta" / "manifest.json"
    data = json.load(open(path))["versions"]
    path = root() / "meta" / "com.mojang" / "1.16.5.json"
    for i in data:
        if i["id"] == "1.16.5":
            if download(session, i["url"], path, quiet=True) != 0:
                log(f"Failed to download version data for 1.16.5", "ERROR")

    log("Downloading asset index")
    data = json.load(open(root() / "meta" / "net.minecraft" / f"{v}.json"))["assetIndex"]
    if download(session, data["url"], root() / "assets" / "indexes" / f"{data["id"]}.json", data["sha1"], quiet=True) != 0:
        log("Failed to download asset index", "ERROR")

    log("Downloading version JAR")
    data = json.load(open(root() / "meta" / "com.mojang" / f"{v}.json"))["downloads"]["client"]
    if download(session, data["url"], root() / "version" / v / f"{v}.jar", data["sha1"], quiet=True) != 0:
        log("Failed to download version JAR", "ERROR")

    log(f"Minecraft metadata for {v} downloaded")