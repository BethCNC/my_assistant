const {app, BrowserWindow} = require('electron')
const path = require('path')

const createWindow = () => {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, 'frontend/public/assets/smiley.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    titleBarStyle: 'hiddenInset',
    show: false
  })
  
  // Load the app - in dev mode it's localhost:3000, in production it would be the built files
  const isDev = process.env.NODE_ENV === 'development'
  const url = isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, 'frontend/out/index.html')}`
  
  win.loadURL(url)
  
  // Show window when ready to prevent visual flash
  win.once('ready-to-show', () => {
    win.show()
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
}) 