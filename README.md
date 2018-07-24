# wuy 

If you have made a _super python tool_, and you want to add a GUI but without using the biggest qt/gtk/tk/wx/kivy : you are in the right place ! Just re-use the local browser (chrome in app mode) as GUI, drived by **wuy**.

<p align="center"><img src="https://github.com/manatlan/wuy/blob/master/wiki/capture.png"/></p>

Basically, it's a python module which will act as a web server (http & websocket) and will open/manage a window for you ; providing a simple framework (js/py3 helpers).

It lets you create your GUI with yours web skills (html/js/css or any js frameworks/libs), and re-use the power of python on server side.

Technically, it's a python3 module, using asyncio and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/), and (if present) the [uvloop](https://magic.io/blog/uvloop-blazing-fast-python-networking/), for the full speed ! The http server is here to serve static content (html, js, images ...). The websocket is here to simplify the communication (sync/async) between the window & the server. (rpc method to communicate from client to server, pubsub mechanism to communicate from server to clients, or from client to clients)

In **app/window mode** : it will manage (open/close) the window for you ; using the **chrome app mode** ; if the websocket brokes : window & server will shutdown (close the window ; the server will shutdown, close the server ; the window will shutdown). You (or your clients) will not see a difference with classical GUI ! If it can't start a chrome app : it will act as the server mode. 

In **server mode** : it will act as a classical web server ; and you can use as many clients/browsers as you want, from localhost or from anywhere else. Closing a socket ; just close the socket ;-). It can be hosted on the web, as long as the provider service use python3.

In all cases : it will be pretty easy to produce/freeze an executable/windows (one file with all html/js embedded), using [pyinstaller/windows](https://github.com/manatlan/wuy/blob/master/BUILD.bat). And share your _super python tool_ to the world.

For **app/window mode**: the wuy/js will work like a charm in chrome. For **server mode**: you can add [polyfill](https://polyfill.io/v2/docs/) to be able to use a lot of older browsers (IE11, etc ...), see the [tchat](https://github.com/manatlan/wuy/blob/master/web/tchat.html) server.

It's, a little bit, like [python eel](https://github.com/ChrisKnott/Eel).

**TODOs**:
* Write docs & examples

## To Test/Run

Download [the zip from here](https://github.com/manatlan/wuy/archive/master.zip)

    $ pip3 install aiohttp winreg
    $ python3 -u simple.py

(_winreg_ is needed for windows only)

or the new way of doing things, for app/window:

    $ python3 -u an_app.py

For the server 

    $ python3 -u a_server.py

## To Use

Install the lib :

    $ pip3 install wuy winreg

(_winreg_ is needed for windows only)

* See the [old style (like Eel)](https://github.com/manatlan/wuy/blob/master/wiki/old.md) ****DEPRECATED****
* See the [new style](https://github.com/manatlan/wuy/blob/master/wiki/tuto.md)

## See Examples

* [an_app](https://github.com/manatlan/wuy/blob/master/an_app.py) : same as simple.py but in the new fashion
* [an_app2](https://github.com/manatlan/wuy/blob/master/an_app2.py) : an input box
* [an_app3](https://github.com/manatlan/wuy/blob/master/an_app3.py) : an alert box with autodeclared js vars (chain'able windows)!
* [an_app4](https://github.com/manatlan/wuy/blob/master/an_app4.py) : using sync & async rpc calls !
* [an_app5](https://github.com/manatlan/wuy/blob/master/an_app5.py) : using async aiohttp.get (request content from web)
* [an_appVuejs](https://github.com/manatlan/wuy/blob/master/an_appVuejs.py) : using a vuejs app (and  a continuous push from server to client)
* [a_server](https://github.com/manatlan/wuy/blob/master/a_server.py) : a server, tchat service for multiple clients

with **wuy.Window** for app (which open/manage a chrome window app)

with **wuy.Server** for classic http/ws servers

