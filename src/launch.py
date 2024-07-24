import json
import os
import platform
import subprocess

from src.java import get_version
from src.microsoft import *
from src.util import *

USERNAME = "TechnoDot"
UUID = "9a467ecf8eaf4d9cb44050eb9b60581a" # long live my old account
TOKEN = "eynevergonnagiveyouupnevergonnaletyoudownnevergonnarunaroundanddesertyou"

def classpath(data, version):
    sep = ";" if platform.system() == "Windows" else ":"
    cp = ""

    for library in data["libraries"]:
        if "rules" in library and (False if any([parse_rule(i) for i in library["rules"]]) else True): continue
        sections = library["name"].split(":")
        cp += os.path.join(root() / "libraries", convert_path(sections)) + sep

    cp += str(root() / "version" / version / f"{version}.jar")
    return cp

def jvm_arguments(data, version, modern):
    arguments = []

    for argument in modern["arguments"]["jvm"]:
        if isinstance(argument, dict):
            if "rules" in argument and (False if any([parse_rule(i) for i in argument["rules"]]) else True): continue
            arguments.append(argument["value"][0])
    
    arguments += [f"-D{arg}={str(root() / "versions" / version / "natives")}" for arg in ["java.library.path", "jna.tmpdir", "org.lwjgl.system.SharedLibraryExtractPath", "io.netty.native.workdir"]]
    
    arguments += [
        "-Dminecraft.launcher.brand=technoclient",
        "-Dminecraft.launcher.version=1.0",
        "-cp",
        classpath(data, version)
    ]
    
    return arguments

def game_arguments(data, version):
    arguments = data["minecraftArguments"].split(" ") if "minecraftArguments" in data else []

    if arguments == []:
        for argument in data["arguments"]["game"]:
            if not isinstance(argument, dict):
                arguments.append(argument)
            else:
                pass # TODO: implement "features" or whatever
    
    replace = {
        "${auth_player_name}": USERNAME,
        "${version_name}": version,
        "${game_directory}": root() / "minecraft",
        "${assets_root}": root() / "assets",
        "${assets_index_name}": data["assetIndex"]["id"],
        "${auth_uuid}": UUID,
        "${auth_access_token}": TOKEN,
        "${user_type}": "msa",
        "${version_type}": "release" if version.find(".") != -1 else "snapshot"
    }

    for i, argument in enumerate(arguments):
        if argument in replace:
            arguments[i] = replace[argument]
    
    return arguments

def run(version, session):
    v = version.split("-")[0]

    _, java_version = get_version(version)

    with open(root() / "meta" / "com.mojang" / f"{v}.json") as file:
        data = json.load(file)
    
    with open(root() / "meta" / "com.mojang" / "1.16.5.json") as file:
        modern_data = json.load(file)

    command = [{
        "Windows": root() / "java" / java_version / "bin" / "java.exe",
        "Darwin": root() / "java" / java_version / f"zulu-{java_version}.jre" / "Contents " / "Home" / "bin" / "java",
        "Linux": root() / "java" / java_version / "bin" / "java"
    }[platform.system()]]

    command += jvm_arguments(data, v, modern_data)
    command.append(data["mainClass"])
    command += game_arguments(data, v)

    log(f"Launching game ({version})")
    print("=" * 80)

    subprocess.run(command)
