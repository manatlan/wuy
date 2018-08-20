@ECHO OFF
c:\Python3\Scripts\pyinstaller.exe an_app.py --noupx --onefile --noconsole --add-data="web;web"
REM $ pyinstaller an_app.py --noupx --onefile --noconsole --add-data="web:web"
pause
