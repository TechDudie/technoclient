import argparse
import requests

import src.server as server
import src.version as version
import src.java as java

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
        
        case "java":
            match args.action:
                case "install":
                    java.install(args.version, s)

                case _:
                    log("Invalid action specified", "ERROR")

        case _:
            log("Invalid module specified", "ERROR")