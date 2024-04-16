const { app, BrowserWindow } = require('electron')
const path = require('path')

let windowGlobal

function centerInMain() {
    try {
        windowGlobal.moveTop()
        windowGlobal.setPosition(0, 0)
        windowGlobal.setFullScreen(true)
    } catch (e) {
        console.error(e)
    }
}

function setUpIpc() {
    const { ipcMain } = require('electron')
    for (let [ev, fn] of Object.entries({
        'send': (_, event, data) => {
            switch (event) {
                case "openDevTools":
                    windowGlobal.webContents.openDevTools()
                    break
                case "minMax":
                    if (data.minimize) return windowGlobal.setPosition(0, -200000)
                    if (data.restore) return centerInMain()
                    break
            }
        }
    })) ipcMain.on(ev, fn)
}

function createWindow() {
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
    windowGlobal.setIgnoreMouseEvents(true);
    windowGlobal.loadFile('index.html')
    centerInMain()
    setUpIpc()
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
