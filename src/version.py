import hashlib
import json
import os
import re
import warnings
warnings.filterwarnings("ignore")
import requests

VANILLA_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
FORGE_MANIFEST_URL = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/maven-metadata.xml"
FABRIC_MANIFEST_URL = "https://meta.fabricmc.net/v2/versions/loader"

FORGE_INSTALLER_URL = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/VERSION/forge-VERSION-installer.jar"
FABRIC_INSTALLER_URL = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/VERSION/fabric-installer-VERSION.jar"

MANIFEST_URL = {
    "vanilla": VANILLA_MANIFEST_URL,
    "forge": FORGE_MANIFEST_URL,
    "fabric": FABRIC_MANIFEST_URL
}

INSTALLER_URL = {
    "vanilla": None,
    "forge": FORGE_INSTALLER_URL,
    "fabric": FABRIC_INSTALLER_URL
}

def convert_version_vanilla(directory, vanilla):
    with open(f"{directory}/versions/manifest_vanilla.json") as file:
        manifest = json.load(file)

    target = vanilla
    if vanilla in ["release", "snapshot"]:
        target = ["latest"][vanilla]
    
    for version in manifest["versions"]:
        if version["id"] == target:
            return version["id"]

def convert_version_forge(directory, vanilla):
    with open(f"{directory}/versions/manifest_forge.json") as file:
        manifest = file.read()

    forge =  {
        "release": re.search("(?<=<release>).*?(?=</release>)", manifest, re.MULTILINE).group(),
        "latest": re.search("(?<=<latest>).*?(?=</latest>)", manifest, re.MULTILINE).group(),
        "versions": re.findall("(?<=<version>).*?(?=</version>)", manifest, re.MULTILINE)
    }

    if vanilla in ["release", "latest"]:
        return forge[vanilla]
    
    for version in forge["versions"]:
        if version.startswith(vanilla):
            return "-".join(version.split("-")[:2])

def convert_version_fabric(directory, vanilla):
    with open(f"{directory}/versions/manifest_fabric.json") as file:
        manifest = json.load(file)
    
    # TODO

def download(url, path, proxy=None, sha1=None):
    proxies = {"http": f"socks5h://{proxy}", "https": f"socks5h://{proxy}", "socks5": f"socks5h://{proxy}"} if proxy else None
    r = requests.get(url, proxies=proxies)
    if r.status_code == 200:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file: file.write(r.content)
    
    if sha1:
        with open(path, "rb") as file: return int(not hashlib.sha1(file.read()).hexdigest() == sha1)

def run(directory, version, proxy, version_type="vanilla"):
    # TODO: Forge and Fabric

    manifest_path = f"{directory}/versions/manifest_{version_type}.json"
    download(MANIFEST_URL[version_type], manifest_path, proxy=proxy)
    
    if version_type == "vanilla":
        version = convert_version_vanilla(version)
        version_path = f"{directory}/versions/{version}/{version}.json"

        with open(manifest_path) as file:
            versions = json.load(file)["versions"]
        
        for v in versions:
            if v["id"] == version:
                download(v["url"], version_path, proxy, v["sha1"])
                break
        
        with open(version_path) as file:
            data = json.load(file)
            client_data = data["downloads"]["client"]
            logging_data = data["logging"]["client"]["file"]
        
        download(client_data["url"], f"{directory}/versions/{version}/{version}.jar", proxy, client_data["sha1"])
        download(logging_data["url"], f"{directory}/config/{logging_data['id']}", proxy, logging_data["sha1"])
    if version_type == "forge":
        version = convert_version_forge(version)
    if version_type == "fabric":
        version = convert_version_fabric(version)
    
    print(f"\n\nMinecraft manifests for {version} installed successfully!")
