# wuy 

It's like [python eel](https://github.com/ChrisKnott/Eel) BUT :

* it uses asyncio, and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/) and [uvloop](https://magic.io/blog/uvloop-blazing-fast-python-networking/) if present.
* it uses python3 ONLY
* it's server hosted friendly from scratch (use wuy.Server) (but not IE11 compatible)
* it uses pubsub mechanism to communicate from server to clients, or from client to clients
* it can call sync or async rpc method on the server
* it's pyinstaller-friendly on windows, see [bat file](https://github.com/manatlan/wuy/blob/master/COMPILE.bat)
* com errors are catch'able with the promise
* a wuy.Window can open another wuy.Window during a rpc call

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

    python3 web.py

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

    python3 web.py

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

