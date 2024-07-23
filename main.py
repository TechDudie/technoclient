import argparse
import requests

import src.assets as assets
import src.libraries as libraries
import src.launch as launch
import src.java as java
import src.server as server
import src.version as version

from src.util import *

if __name__ == "__main__":

    if default():
        log("Getting things ready...")

        server.default()

        log("Setup complete")

        exit()

    parser = argparse.ArgumentParser(
        prog="technoclient-core", # TODO: move backend into `launchcraft` repository
        description="TechnoClient core module; the backend stuff that makes everything work"
    )

    parser.add_argument(
        "-p", "--proxy",
        type=str
    )

    parser.add_argument(
        "module",
        type=str
    )

    parser.add_argument(
        "action",
        type=str
    )

    parser.add_argument(
        "version",
        type=str,
        nargs="?",
        default=""
    )

    args = parser.parse_args()

    if args.proxy:
        s = requests.Session(proxies={"http": f"socks5h://{args.proxy}", "https": f"socks5h://{args.proxy}", "socks5": f"socks5h://{args.proxy}"})
    else:
        s = requests.Session()

    match args.module:
        
        case "server":
            match args.action:
                case "refresh":
                    server.refresh()
        
        case "metadata":
            match args.action:
                case "update":
                    version.run(args.version, s)
        
        case "assets":
            match args.action:
                case "install":
                    assets.run(args.version, s)
        
        case "libraries":
            match args.action:
                case "install":
                    libraries.run(args.version, s)
        
        case "java":
            match args.action:
                case "install":
                    java.run(args.version, s)
        
        case "launch":
            match args.action:
                case "run":
                    launch.run(args.version, s)

        case _:
            log("Invalid module specified", "ERROR")