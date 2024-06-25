const { app, BrowserWindow } = require('electron')
const path = require('node:path')

function setupWindow() {
    const root = new BrowserWindow({
        width: 854,
        height: 512,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })

    root.loadFile('src/html/index.html')

    root.removeMenu()

    // root.webContents.openDevTools() // only for when I'm a stupidhead :/
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