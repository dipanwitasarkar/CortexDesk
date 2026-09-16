import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  // Add any IPC methods here if needed
  // For example:
  // sendMessage: (message: string) => ipcRenderer.invoke('send-message', message),
})
