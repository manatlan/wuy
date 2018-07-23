# wuy 

You have made a _super python tool_, and you want to add a GUI but without using the bigger qt/gtk/tk/wx/kivy. You are in the right place ! Just re-use the local browser (chrome in app mode) as GUI, drived by **wuy**.

Basically, it's a python module which will act as a web server (http & websocket) and will open/manage a window for you ; providing a simple framework (js/py3 helpers).

It lets you create your GUI with yours web skills (html/js/css or any js frameworks/libs), and re-use the power of python on server side.

Technically, it's a python3 module, using asyncio and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/), and (if present) the [uvloop](https://magic.io/blog/uvloop-blazing-fast-python-networking/), for the full speed ! The http server is here to serve static content (html, js, images ...). The websocket is here to simplify the communication (sync/async) between the window & the server.

In **app/window mode** : it will manage (open/close) the window for you ; using the **chrome app mode** ; if the websocket brokes : window & server will shutdown (close the window ; the server will shutdown, close the server ; the window will shutdown). You (or your clients) will not see a difference with classical GUI ! If it can't start a chrome app : it will act as the server mode. 

In **server mode** : it will act as a classical web server ; and you can use as many clients/browsers as you want, from localhost or from anywhere else. Closing a socket ; just close the socket ;-). It can be hosted on the web, as long as the provider service use python3.

In all cases : it will be pretty easy to produce/freeze an executable/windows (one file with all html/js embedded), using [pyinstaller/windows](https://github.com/manatlan/wuy/blob/master/COMPILE.bat). And share your _super python tool_ to the world.

It's, a little bit, like [python eel](https://github.com/ChrisKnott/Eel).

**TODOs**:
* Make JS compatible with (the old) IE11 too.
* Write docs

## to test/run

Download [the zip from here](https://github.com/manatlan/wuy/archive/master.zip)

    $ pip3 install aiohttp
    $ python3 -u simple.py

or the new way of doing things, for app/window:

    $ python3 -u an_app.py

For the server 

    $ python3 -u a_server.py

## to use

Install the lib :

    $ pip3 install wuy

create a python file "web.py", and copy/paste this:

```python
import wuy
wuy.start(app=True)
```
Run it, like this :

    $ python3 web.py

It will create a "web/index.html", the defaut front-end ;-)

Edit "web/index.html", like this :

```html
<script src="wuy.js"></script>
<button onclick="wuy.myadd(42,13).then( alert )">test</button>
```

Edit "web.py", like this :

```python
import wuy

@wuy.expose
def myadd(a,b):
    return a+b

wuy.start(app=(640,480))
```

and rerun your script :

    $ python3 web.py

and you can start to code

## but the future is ... bright ;-)

See examples :

* [an_app](https://github.com/manatlan/wuy/blob/master/an_app.py) : same as simple.py but in the new fashion
* [an_app2](https://github.com/manatlan/wuy/blob/master/an_app2.py) : an input box
* [an_app3](https://github.com/manatlan/wuy/blob/master/an_app3.py) : an alert box with autodeclared js vars !
* [an_app4](https://github.com/manatlan/wuy/blob/master/an_app4.py) : using sync & async rpc call !
* [an_app5](https://github.com/manatlan/wuy/blob/master/an_app5.py) : using a continuous push from server to client
* [a_server](https://github.com/manatlan/wuy/blob/master/a_server.py) : a server, tchat service for multiple clients

with **wuy.Window** for app (which open/manage a chrome window app)

with **wuy.Server** for classic http/ws servers

