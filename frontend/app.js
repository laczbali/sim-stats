const { app, BrowserWindow } = require('electron')
const url = require("url");
const path = require("path");

let mainWindow

function createWindow() {
    loadBackend();

    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    })

    mainWindow.loadURL(
        url.format({
            pathname: path.join(__dirname, `/dist/frontend/index.html`),
            protocol: "file:",
            slashes: true
        })
    );
    // Open the DevTools.
    mainWindow.webContents.openDevTools()

    mainWindow.on('closed', function () {
        mainWindow = null
    })
}

function loadBackend() {
    const { spawn } = require('child_process');
    const backend = spawn('python', ['D:\\git\\sim-stats\\backend\\main.py']);

    backend.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
      });
      
    backend.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
    
    backend.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
}

app.on('ready', createWindow)

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
    if (mainWindow === null) createWindow()
})