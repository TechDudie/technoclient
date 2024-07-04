import json
from mcstatus import JavaServer

from src.util import *

{
    [
        {
            "name": "Hypixel",
            "ip": "mc.hypixel.net",
            "version": "1.8.9-default",
            "ping": 0,
            "players": [],
            "favicon": ""
        },
        {
            "name": "Hypixel Skyblock",
            "ip": "mc.hypixel.net",
            "version": "1.8.9-skyblock",
            "ping": 0,
            "players": [],
            "favicon": ""
        },
        {
            "name": "Wynncraft",
            "ip": "play.wynncraft.com",
            "version": "1.21-wynncraft",
            "ping": 0,
            "players": [],
            "favicon": ""
        },
    ]
}

def refresh():
    servers = json.load(open(root() / "servers.json"))

    for server in servers:
        try:
            query = JavaServer.lookup(server["ip"])
            server.ping = query.ping()

        except:
            pass
    