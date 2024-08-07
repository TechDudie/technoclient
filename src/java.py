import hashlib
import os
import platform
import shutil
import subprocess
import zipfile

from src.util import *

def run(version, s):
    azul_version, java_version, data = get_java_version(version)

    log("Retrieving system information")
    
    uname = platform.uname()
    operating_system = {"Windows": "win", "Darwin": "macosx", "Linux": "linux"}[uname[0]]
    processor_architecture = {"x86_64": "x64", "X86_64": "x64", "AMD64": "x64", "ARM64": "aarch64"}["".join([i if i in uname[4] else "" for i in ["x86_64", "X86_64", "AMD64", "ARM64"]])]
    url = f"https://cdn.azul.com/zulu/bin/zulu{azul_version}-ca-jre{java_version}-{operating_system}_{processor_architecture}.zip"
    cache = root() / "cache" / f"zulu{azul_version}-ca-jre{java_version}-{operating_system}_{processor_architecture}.zip"
    path = root() / "cache" / "java"
    target = root() / "java" / java_version
    executable = {
        "Windows": target / "bin" / "java.exe",
        "Darwin": target / f"zulu-{java_version}.jre" / "Contents " / "Home" / "bin" / "java",
        "Linux": target / "bin" / "java"
    }[uname[0]]

    try:
        os_identifier = {
            "winx64": "windows-x64",
            "macosx-64": "mac-os-x64",
            "macosxaarch64": "mac-os-arm64",
            "linux64": "linux-x64"
        }[operating_system + processor_architecture]
        hash = [i for i in data if i["name"] == data[0]["name"] and i["runtimeOS"] == os_identifier][0]["checksum"]["hash"]
    except:
        log("No hash data found for this platform, unable to verify file integrity", "WARN")
        hash = ""

    os.makedirs(os.path.dirname(cache), exist_ok=True)

    log(f"Detected OS: {uname[0].replace('Darwin', 'MacOS')}")
    log(f"Detected Architecture: {processor_architecture}")
    log(f"Downloading Java {java_version} Azul Zulu {azul_version} JRE from {url}")

    r = s.get(url)
    if r.status_code == 200:
        with open(cache, "wb") as file:
            file.write(r.content)
    else:
        log("Unable to download Java", "ERROR")
    
    if hash != "":
        log("Verifying file integrity")

        with open(cache, "rb") as file:
            file_hash = hashlib.sha256(file.read()).hexdigest()
            if file_hash != hash:
                log(f"Downloaded: {file_hash} Metadata: {hash}")
                log("SHA256 verification failed, downloaded file is corrupted", "ERROR")

    with zipfile.ZipFile(cache) as file:
        file.extractall(path)
    
    try:
        shutil.rmtree(target)
    except FileNotFoundError:
        pass
    
    shutil.move(path / f"zulu{azul_version}-ca-jre{java_version}-{operating_system}_{processor_architecture}", target)
    log(f"Extracted contents to {target}")

    if uname[0] != "Windows":
        subprocess.run(["chmod", "+x", executable])
    
    if uname[0] == "Darwin":
        subprocess.run(["xattr", "-d", "com.apple.quarantine", executable])

    log(f"Testing Java {java_version} Azul Zulu {azul_version} JRE")

    print("=" * 80)
    subprocess.run([executable, "-version"])
    print("=" * 80)
    
    log(f"Java {java_version} Azul Zulu {azul_version} JRE installed successfully!")
