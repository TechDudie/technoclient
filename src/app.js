const { app, BrowserWindow } = require('electron')
const path = require('node:path')

const ipc = require('./ipc.js')
const readServerList = require('./serverlist.js')

const devTools = false

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

    if (devTools) {
        root.webContents.openDevTools()
    }

    return root
}

app.whenReady().then(() => {
    let root = setupWindow()

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) setupWindow()
    })

    ipc.initializeIPC(root)

    readServerList()
})

app.on('window-all-closed', function () {
    app.quit()
})
