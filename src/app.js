const { app, BrowserWindow } = require('electron')
const ipc = require('electron').ipcMain
const path = require('node:path')

function setupWindow() {
    const root = new BrowserWindow({
        width: 854,
        height: 512,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false
        }
    })

    root.loadFile('src/html/index.html')

    root.removeMenu()

    // root.webContents.openDevTools()
}

app.whenReady().then(() => {
    setupWindow()

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) setupWindow()
    })
})

app.on('window-all-closed', function () {
    app.quit()
})

ipc.on('quit', () => {
    app.quit()
});