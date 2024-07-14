import os
import platform
import shutil
import subprocess
import warnings
import zipfile
warnings.filterwarnings("ignore")
import requests

def run(directory, version, proxy, java_type="jre"):
    java = {
        "1.20.4": "21",
        "1.8.9": "8",
        "default": "21"
    }

    azul = {
        "21": "21.30.15",
        "8": "8.74.0.17",
        "default": "21.30.15"
    }

    try:
        java_version = java[version]
    except:
        java_version = java["default"]

    try:
        azul_version = azul[java_version]
    except:
        azul_version = azul["default"]

    uname = platform.uname()
    operating_system = {"Windows": "win", "Darwin": "macosx", "Linux": "linux"}[uname[0]]
    processor_architecture = {"X86_64": "x64", "ARM64": "aarch64"}["".join([i if i in uname[3] else "" for i in ["X86_64", "ARM64"]])]
    url = f"https://cdn.azul.com/zulu/bin/zulu21.30.15-ca-{java_type.lower()}21.0.1-{operating_system}_{processor_architecture}.zip"
    cache = f"{directory}/cache/zulu21.30.15-ca-{java_type.lower()}21.0.1-{operating_system}_{processor_architecture}.zip"
    path = f"{directory}/java/"
    target = f"{path}{java_version}"
    executable = {
        "Windows": f"{target}/bin/java.exe",
        "Darwin": f"{target}/zulu-{java_version}.{java_type.lower()}/Contents/Home/bin/java",
        "Linux": f"{target}/bin/java"
    }[uname[0]]


    print(f"Detected OS: {uname[0].replace('Darwin', 'MacOS')}")
    print(f"Detected Architecture: {''.join([i if i in uname[3] else '' for i in ['X86_64', 'ARM64']])}")
    print(f"Downloading Java {java_version} Azul Zulu {azul_version} {java_type.upper()} from {url}")

    r = requests.get(url, proxies={"http": f"socks5h://{proxy}", "https": f"socks5h://{proxy}", "socks5": f"socks5h://{proxy}"})
    if r.status_code == 200:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(cache, "wb") as file: file.write(r.content)
    else:
        print("Unable to download Java. Please submit an issue with the following information:")
        print(f"Detected OS: {uname[0].replace('Darwin', 'MacOS')}")
        print(f"Detected Architecture: {''.join([i if i in uname[3] else '' for i in ['X86_64', 'ARM64']])}")
        print(f"Minecraft Version: {version}")
        print(f"Java Version: {java_version}")
        print(f"Azul Version: {azul_version}")
        print(f"Java Type: {java_type}")
        exit(1)

    with zipfile.ZipFile(cache) as file:
        file.extractall(path)

    shutil.move(f"{directory}/java/zulu21.30.15-ca-{java_type.lower()}21.0.1-{operating_system}_{processor_architecture}", target)

    if uname[0] != "Windows":
        subprocess.run(["chmod", "+x", executable])
    
    if uname[0] == "Darwin":
        subprocess.run(["xattr", "-d", "com.apple.quarantine", executable])

    print(f"Testing Java {java_version} Azul Zulu {azul_version} {java_type.upper()}")

    subprocess.run([executable, "-version"])

    print(f"\n\nJava {java_version} Azul Zulu {azul_version} {java_type.upper()} installed successfully!")
