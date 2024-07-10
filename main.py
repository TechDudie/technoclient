import argparse

import src.server as server

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
        "module",
        type=str
    )

    parser.add_argument(
        "action",
        type=str
    )

    args = parser.parse_args()

    match args.module:
        
        case "server":
            match args.action:
                case "refresh":
                    server.refresh()
                
                case _:
                    log("Invalid action specified", "ERROR")

        case _:
            log("Invalid module specified", "ERROR")