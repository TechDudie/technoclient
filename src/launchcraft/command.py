import json
import os
import platform
import re
import subprocess
import sys

USERNAME = "TechnoDot"
UUID = "9a467ecf8eaf4d9cb44050eb9b60581a"
TOKEN = "eynevergonnagiveyouupnevergonnaletyoudownnevergonnarunaroundanddesertyou"

def parse_rule(rule, options) -> bool:
    if rule["action"] == "allow": value = False
    elif rule["action"] == "disallow": value = True

    for os_key, os_value in rule.get("os", {}).items():
        if os_key == "name":
            if os_value == "windows" and platform.system() != 'Windows': return value
            elif os_value == "osx" and platform.system() != 'Darwin': return value
            elif os_value == "linux" and platform.system() != 'Linux': return value
        elif os_key == "arch" and os_value == "x86" and platform.architecture()[0] != "32bit": return value
        elif os_key == "version" and not re.match(os_value, f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}" if platform.system() == "Windows" else platform.uname().release): return value

    return not value

def classpath(data, version, directory):
    sep = ";" if platform.system() == "Windows" else ":"
    libraries = ""

    for library in data["libraries"]:
        if "rules" in library and (False if any([parse_rule(i, {}) for i in library["rules"]]) else True): continue
        sections = library["name"].split(":")
        libraries += f"{directory}/libraries/{'/'.join(sections[0].split('.'))}/{sections[1]}/{sections[2]}/{sections[1]}-{sections[2]}{'-' + sections[3] if 3 < len(sections) else ''}.jar{sep}"

    libraries += f"{directory}/versions/{version}/{version}.jar"
    return libraries

def jvm_arguments(data, version, directory):
    arguments = []
    
    for argument in data["arguments"]["jvm"]:
        if isinstance(argument, dict):
            if "rules" in argument and (False if any([parse_rule(i, {}) for i in argument["rules"]]) else True): continue
            arguments.append(argument["value"][0])
        else:
            if argument.find("${natives_directory}") != -1:
                arguments.append(argument.replace("${natives_directory}", f"{directory}/versions/{version}/natives"))
            elif argument.find("${launcher_name}") != -1:
                arguments.append(argument.replace("${launcher_name}", "technolauncher"))
            elif argument.find("${launcher_version}") != -1:
                arguments.append(argument.replace("${launcher_version}", "1.0"))
            elif argument.find("${classpath}") != -1:
                arguments.append("-cp")
                arguments.append(argument.replace("${classpath}", classpath(data, version, directory)))
    
    return arguments

def game_arguments(data, version, directory):
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
            arguments[i] = f"{directory}/game"
        elif argument == "${assets_root}":
            arguments[i] = f"{directory}/assets"
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
def run(directory, version, proxy, java_type="jre"):
    directory = "/Users/3124224/Library/Application Support/devnolauncher"
    version = "1.20.4"

    java = {
        "1.20.4": "21",
        "1.8.9": "8",
        "default": "21"
    }

    try:
        java_version = java[version]
    except:
        java_version = java["default"]

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
