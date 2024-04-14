const { app, BrowserWindow } = require('electron')
const path = require('path')

/*
function returnMonitorList()
function fullscrenOnMonitor()
*/

let windowGlobal

const centerInMain = () => {
    try {
        windowGlobal.moveTop()
        windowGlobal.setPosition(0, 0)
        windowGlobal.setFullScreen(true)
    } catch (e) {
        console.error(e)
    }
}

const setUpIpc = () => {
    const { ipcMain } = require('electron')
    const ipcEvents = {
        'send': (_, event, data) => {
            switch (event) {
                case "openDevTools":
                    windowGlobal.webContents.openDevTools()
                    break
                case "minMax":
                    if (data.minimize) {
                        windowGlobal.setPosition(0, -200000)
                    }
                    else if (data.restore) {
                        centerInMain()
                    }
                    break
            }
        }
    }
    for (let [ev, fn] of Object.entries(ipcEvents)) ipcMain.on(ev, fn)
}

const createWindow = () => {
    windowGlobal = new BrowserWindow({
        width: 777,
        height: 777,
        frame: false,
        alwaysOnTop: true,
        transparent: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })
    windowGlobal.setSkipTaskbar(true);
    // windowGlobal.
    windowGlobal.setIgnoreMouseEvents(true);
    windowGlobal.loadURL('https://xyzKey.wumbl3.xyz/xyzKey/init.html')
    centerInMain()
    setUpIpc()
    // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
    createWindow()
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})
