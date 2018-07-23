# -*- coding: utf-8 -*-
import sys
import winreg
import webbrowser

def getChrome():
    def getExe():
        if sys.platform in ['win32', 'win64']:
            return find_chrome_win()
        elif sys.platform == 'darwin':
            return find_chrome_mac()

    exe=getExe()
    if exe:
        return webbrowser.GenericBrowser(exe)
    else:
        webbrowser._tryorder=['google-chrome','chrome',"chromium","chromium-browser"]
        try:
            return webbrowser.get()
        except webbrowser.Error:
            return None

def find_chrome_win():
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
    for install_type in winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE:
        try:
            with winreg.OpenKey(install_type, reg_path, 0, winreg.KEY_READ) as reg_key:
                return winreg.QueryValue(reg_key, None)
        except WindowsError:
            pass

def find_chrome_mac():
    default_dir = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.path.exists(default_dir):
        return default_dir

def openApp(url):
    chrome=getChrome()
    if chrome:
        chrome.args=["--app="+url]
        return chrome.open(url, new=1, autoraise=True)

if __name__=="__main__":
    openApp("http://manatlan.com")
