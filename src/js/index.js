const ipc = require('electron').ipcRenderer

const _version = "1.0.0"

screens = [
    "_main",
    "_multiplayer"
];

function e(id) {
    return document.getElementById(id)
}

function view(screen) {
    screens.forEach((id) => {
        if (id != screen) {
            e(id).style.display = "none"
        }
    });
    e(screen).style.display = "block"
}

document.getElementById("subheader").innerText = _version

e("quit").addEventListener('click', () => {
    ipc.send("quit", "")
});

e("servers").addEventListener('click', () => {
    view("_multiplayer")
    ipc.send("screen", "_multiplayer")
});

Array.from(document.getElementsByClassName("back")).forEach((element) => {
    element.addEventListener('click', () => {
        view("_main")
        ipc.send("screen", "_main")
    });
});

// serverlist

ipc.on("serverlist", (event, data) => {
    let i = 0

    data.forEach((server) => {
        e("serverlist").innerHTML += `<div class="server">
    <img class="server_icon" src="${server["favicon"]}">
    <span class="server_name">${server["name"]}</span>
    <span class="server_ip">IP: <span class="ip">${server["ip"]}</span></span>
    <span class="server_version">Version: ${server["version"]}</span>
    <span class="server_capacity">${server["playercount"][0]}/${server["playercount"][1]}</span>
    <span class="server_ping">${server["ping"]}ms</span>
    <button class="server_edit"><span>Edit</span></button>
    <button class="server_join"><span>Join</span></button>
</div>`
        element = document.getElementsByClassName("server_ping")[i]

        if (server["ping"] == -1) {
            element.innerHTML = "?ms"
            element.style.color = "#ffffff"
        } else if (server["ping"] < 50) {
            element.style.color = "#30b840"
        } else if (server["ping"] < 300) {
            element.style.color = "#edde37"
        } else {
            element.style.color = "#ee3322"
        }

        i += 1
    })
})
