// Module to control the application lifecycle and the native browser window.
const { app, BrowserWindow, protocol, ipcMain } = require("electron");
const path = require("path");
const url = require("url");
const util = require('node:util');
const { exec, execFile } = require('node:child_process');
const controller = new AbortController();
const { signal } = controller;
const axios = require("axios");


// Create the native browser window.
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 900,
    // Set the path of an additional "preload" script that can be used to
    // communicate between node-land and browser-land.
    title: 'CO2 Pipeline Routing Tool',
    icon: 'icon.png',
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      nativeWindowOpen: true
    },
  });
  
  // prevent the window title from reverting back to the default, 'React App'
  mainWindow.on('page-title-updated', (e) => {
    e.preventDefault();
  })

  // In production, set the initial browser path to the local bundle generated
  // by the Create React App build process.
  // In development, set it to localhost to allow live/hot-reloading.
  const appURL = app.isPackaged
    ? url.format({
        pathname: path.join(__dirname, "index.html"),
        protocol: "file:",
        slashes: true,
      })
    : "http://localhost:3000";
  mainWindow.loadURL(appURL);
  console.log(process.execPath);
  if (app.isPackaged){
    const exe_path = path.join(__dirname, '../../../dist/CO2PRT_Flask/CO2PRT_Flask.exe')
    // const exe_path = path.join(process.execPath, '/CO2PRT_Flask.exe')
    var child = execFile(exe_path, [],(error, stdout, stderr) => {
      console.log(exe_path);
      if (error) {
        console.log(stdout);
        console.log(stderr);
        throw error;
      }
      console.log(stdout);
    });
  }else{
    const exe_path = path.join(process.execPath, '/CO2PRT_Flask.exe')
    console.log(exe_path);

  }

  // Automatically open Chrome's DevTools in development mode.
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
  mainWindow.on('close', function(e) {
    e.preventDefault();
    mainWindow.destroy();
    if (app.isPackaged) {
      axios.get('/exit');
      child.kill();
    }
  })
  /// Removing below fixed the issue with a javascript error when closing the window
  // mainWindow.on('closed', function() {
  //   mainWindow = null
  // })

}


// Setup a local proxy to adjust the paths of requested files when loading
// them from the local production bundle (e.g.: local fonts, etc...).
function setupLocalFilesNormalizerProxy() {
  protocol.registerHttpProtocol(
    "file",
    (request, callback) => {
      const url = request.url.substr(8);
      callback({ path: path.normalize(`${__dirname}/${url}`) });
    },
    (error) => {
      if (error) console.error("Failed to register protocol");
    },
  );
}
 
// This method will be called when Electron has finished its initialization and
// is ready to create the browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow();
  setupLocalFilesNormalizerProxy();
 
  app.on("activate", function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});
 
// attempt 3 at showing help doc
// app.on('web-contents-created', (createEvent, contents) => {
//   contents.setWindowOpenHandler(({ url }) => {
//     console.log(url);
//     if (url.startsWith('http://')) {
//       exec(path.join(__dirname, "documentation/_build/html/index.html"))
//     }
//     return { action: 'deny' }
//   });
// });

// Quit when all windows are closed, except on macOS.
// There, it's common for applications and their menu bar to stay active until
// the user quits  explicitly with Cmd + Q.
app.on("window-all-closed", function () {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
 
// If your app has no need to navigate or only needs to navigate to known pages,
// it is a good idea to limit navigation outright to that known scope,
// disallowing any other kinds of navigation.
const allowedNavigationDestinations = "https://my-electron-app.com";
app.on("web-contents-created", (event, contents) => {
  contents.on("will-navigate", (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
 
    if (!allowedNavigationDestinations.includes(parsedUrl.origin)) {
      event.preventDefault();
    }
  });
});
 
// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here. 
