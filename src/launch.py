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
        cp += os.path.join(root(), convert_path(sections)) + sep

    cp += str(root() / "version" / version / f"{version}.jar")
    return cp

def jvm_arguments(data, version):
    arguments = []

    for argument in data["arguments"]["jvm"]:
        if isinstance(argument, dict):
            if "rules" in argument and (False if any([parse_rule(i) for i in argument["rules"]]) else True): continue
            arguments.append(argument["value"][0])
        else:
            if argument.find("${natives_directory}") != -1:
                arguments.append(argument.replace("${natives_directory}", str(root() / "versions" / version / "natives")))
            elif argument.find("${launcher_name}") != -1:
                arguments.append(argument.replace("${launcher_name}", "technoclient"))
            elif argument.find("${launcher_version}") != -1:
                arguments.append(argument.replace("${launcher_version}", "1.0"))
            elif argument.find("${classpath}") != -1:
                arguments.append("-cp")
                arguments.append(argument.replace("${classpath}", classpath(data, version)))
    
    return arguments

def game_arguments(data, version):
    arguments = []
    
    for argument in data["arguments"]["game"]:
        if not isinstance(argument, dict):
            arguments.append(argument)
    
    for i, argument in enumerate(arguments):
        if argument == "${auth_player_name}":
            arguments[i] = USERNAME
        elif argument == "${version_name}":
            arguments[i] = version
        elif argument == "${game_directory}":
            arguments[i] = root() / "minecraft"
        elif argument == "${assets_root}":
            arguments[i] = root() / "assets"
        elif argument == "${assets_index_name}":
            arguments[i] = data["assetIndex"]["id"]
        elif argument == "${auth_uuid}":
            arguments[i] = UUID
        elif argument == "${auth_access_token}":
            arguments[i] = TOKEN
        elif argument == "${user_type}":
            arguments[i] = "msa"
        elif argument == "${version_type}":
            arguments[i] = "release" if version.find(".") != -1 else "snapshot"

    return arguments

def run(version, session):
    v = version.split("-")[0]

    _, java_version = get_version(version)

    with open(root() / "meta" / "com.mojang" / f"{v}.json") as file:
        data = json.load(file)

    command = [{
        "Windows": root() / "java" / java_version / "bin" / "java.exe",
        "Darwin": root() / "java" / java_version / f"zulu-{java_version}.jre" / "Contents " / "Home" / "bin" / "java",
        "Linux": root() / "java" / java_version / "bin" / "java"
    }[platform.system()]]

    command += jvm_arguments(data, v)
    command.append(data["mainClass"])
    command += game_arguments(data, v)

    print(command)

    log(f"Launching game ({version})")
    print("=" * 80)

    subprocess.run(command)
