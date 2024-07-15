import os
import platform
import shutil
import subprocess
import zipfile

from src.util import *

# TODO: get the latest Java 21 LTS version with its corresponding Azul version?
JAVA_VERSION = "21.0.3"
AZUL_VERSION = "21.34.19"

def install(version, s):
    # Just kidding, we dont care what the mc version is

    uname = platform.uname()
    operating_system = {"Windows": "win", "Darwin": "macosx", "Linux": "linux"}[uname[0]]
    processor_architecture = {"X86_64": "x64", "AMD64": "x64", "ARM64": "aarch64"}["".join([i if i in uname[4] else "" for i in ["X86_64", "AMD64", "ARM64"]])]
    url = f"https://cdn.azul.com/zulu/bin/zulu{AZUL_VERSION}-ca-jre{JAVA_VERSION}-{operating_system}_{processor_architecture}.zip"
    cache = root() / "cache" / f"zulu{AZUL_VERSION}-ca-jre{JAVA_VERSION}-{operating_system}_{processor_architecture}.zip"
    path = root() / "cache" / "java"
    target = path / JAVA_VERSION
    executable = {
        "Windows": target / "bin" / "java.exe",
        "Darwin": target / "zulu-{JAVA_VERSION}.jre" / "Contents " / "Home" / "bin" / "java",
        "Linux": target / "bin" / "java"
    }[uname[0]]

    log(f"Detected OS: {uname[0].replace('Darwin', 'MacOS')}")
    log(f"Detected Architecture: {processor_architecture}")
    log(f"Downloading Java {JAVA_VERSION} Azul Zulu {AZUL_VERSION} JRE from {url}")

    r = s.get(url)
    if r.status_code == 200:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(cache, "wb") as file: file.write(r.content)
    else:
        log("Unable to download Java.", "ERROR")

    with zipfile.ZipFile(cache) as file:
        file.extractall(path)
    
    shutil.rmtree(target)
    shutil.move(path / f"zulu{AZUL_VERSION}-ca-jre{JAVA_VERSION}-{operating_system}_{processor_architecture}", target)
    log(f"Extracted contents to {target}")

    if uname[0] != "Windows":
        subprocess.run(["chmod", "+x", executable])
    
    if uname[0] == "Darwin":
        subprocess.run(["xattr", "-d", "com.apple.quarantine", executable])

    log(f"Testing Java {JAVA_VERSION} Azul Zulu {AZUL_VERSION} JRE")

    print("=" * 80)
    subprocess.run([executable, "-version"])
    print("=" * 80)
    
    log(f"Java {JAVA_VERSION} Azul Zulu {AZUL_VERSION} JRE installed successfully!")
