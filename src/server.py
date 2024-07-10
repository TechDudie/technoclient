import json
import mcstatus

from src.util import *

def default():
    json.dump({
        "servers": [
            {
                "name": "Hypixel",
                "ip": "mc.hypixel.net",
                "version": "1.8.9-default",
                "ping": -1,
                "playercount": (0, 0),
                "players": [],
                "favicon": "",
            },
            {
                "name": "Wynncraft",
                "ip": "play.wynncraft.com",
                "version": "1.21-wynncraft",
                "ping": -1,
                "playercount": (0, 0),
                "players": [],
                "favicon": ""
            },
        ]
    }, open(root() / "servers.json", "w"))

def refresh():
    servers = json.load(open(root() / "servers.json"))

    # TODO: multithreaded server query
    for i, server in enumerate(servers["servers"]):

        try:
            query = mcstatus.JavaServer.lookup(server["ip"])
            status = query.status().raw
        except:
            log(f"Failed to query {server['name']} ({server['ip']})")

            server["ping"] = -1
            server["playercount"] = (0, 0)
            server["players"] = []
            server["favicon"] = ""

            servers["servers"][i] = server
            continue

        try:
            server["ping"] = query.ping()
        except OSError:
            server["ping"] = -1

        try:
            server["playercount"] = (status["players"]["online"], status["players"]["max"])
        except KeyError:
            server["playercount"] = (0, 0)

        try:
            server["playercount"] = (status["players"]["online"], status["players"]["max"])
        except KeyError:
            server["playercount"] = (0, 0)

        try:
            server["players"] = status["players"]["sample"]
        except KeyError:
            server["players"] = []

        try:
            server["favicon"] = status["favicon"]
        except KeyError:
            server["favicon"] = ""

        servers["servers"][i] = server
    
    json.dump(servers, open(root() / "servers.json", "w"))

    log("Updated servers.json")