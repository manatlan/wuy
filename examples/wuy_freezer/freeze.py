#!/usr/bin/env python3
import sys

try:
    from PyInstaller import __main__ as pyi
except:
    print("Please, install pyinstaller (pip3 install pyinstaller)")
    sys.exit(-1)

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("USAGE: freeze.py <app.py>")
        print("Turns your script into executable ;-)")
    else:
        pyi.run( [sys.argv[1],"--noupx","--onefile","--noconsole","--add-data=web:web"] )
