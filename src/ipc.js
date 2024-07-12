const { app } = require('electron')
const ipc = require('electron').ipcMain

let root = null;

module.exports = {
    initializeIPC: initializeIPC,
    sendIPC: sendIPC
}

function initializeIPC(window) {
    root = window;

    // define ipc listeners here

    ipc.on('quit', () => {
        app.quit()
    });
}

function sendIPC(channel, data) {
    root.webContents.send(channel, data);
}