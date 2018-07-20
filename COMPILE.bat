@ECHO OFF
c:\Python3\Scripts\pyinstaller.exe --noupx --onefile server.py --add-data="web/huy.js;web" --add-data="web/index.html;web"
REM ~ c:\Python3\Scripts\pyinstaller.exe web.spec
pause
