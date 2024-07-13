const app = require('electron')
const ipc = require('electron').ipcMain
const window = require('electron').BrowserWindow;

const readServerList = require('./serverlist.js');

module.exports = {
    initializeIPC: initializeIPC,
    sendIPC: sendIPC
}

function initializeIPC() {
    // define ipc listeners here

    ipc.on('quit', () => {
        app.quit()
    });

    ipc.on('screen', (event, screen) => {
        console.log("window changed")
        if (screen == "_multiplayer") {
            sendIPC("serverlist", readServerList())
        }
    })
}

function sendIPC(channel, data) {
    console.log("crap sent")
    window.getFocusedWindow().webContents.send(channel, data)
}