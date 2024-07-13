const fs = require('fs')
const os = require('os')
const path = require('path')

module.exports = readServerList

const serverlist =  os.homedir() + path.sep + ".technoclient" + path.sep + "serverlist.json"

function readServerList() {
    return JSON.parse(fs.readFileSync(serverlist, 'utf8'))["servers"]
}