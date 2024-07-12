const fs = require('fs')
const os = require('os')
const path = require('path')

const ipc = require('./ipc.js')

module.exports = readServerList

const serverlist =  os.homedir() + path.sep + ".technoclient" + path.sep + "serverlist.json"

function readServerList() {
    const list = JSON.parse(fs.readFileSync(serverlist, 'utf8'))["servers"]
    console.log(list)
    ipc.sendIPC('serverlist', list)
}