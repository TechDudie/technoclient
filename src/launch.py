import json
import os
import platform
import re
import subprocess
import sys

from src.util import *
from src.microsoft import *

# reminder to self: just copy of launchcraft version, not fixed up yet
# reminder to self x2: this is python 3.12 there are match case statements now

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

    cp += root() / "version" / version / f"{version}.jar"
    return cp

def jvm_arguments(data, version):
    arguments = []

    for argument in data["aruguments"]["jvm"]:
        if isinstance(argument, dict):
            if "rules" in argument and (False if any([parse_rule(i) for i in argument["rules"]]) else True): continue
            arguments.append(argument["value"][0])
        else:
            if argument.find("${natives_directory}") != -1:
                arguments.append(argument.replace("${natives_directory}", root() / "versions" / version / "natives"))
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

    with open(f"{directory}/versions/{version}/{version}.json") as file:
        data = json.load(file)

    command = [{
        "Windows": f"{directory}/java/{java_version}/bin/java.exe",
        "Darwin": f"{directory}/java/{java_version}/zulu-{java_version}.{java_type.lower()}/Contents/Home/bin/java",
        "Linux": f"{directory}/java/{java_version}/bin/java"
    }[platform.system()]]

    command += jvm_arguments(data, version, directory)
    command.append(data["mainClass"])
    command += game_arguments(data, version, directory)

    print(f"Launching Minecraft {version}...\n\n{'=' * os.get_terminal_size().columns}\n")

    subprocess.run(command)
