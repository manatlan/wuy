# wuy 

It's like [python eel](https://github.com/ChrisKnott/Eel) BUT :

* it's not as polished
* it uses python3 ONLY
* it uses asyncio, and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
* it's server hosted friendly from scratch
* it uses pubsub mechanism to communicate from server to clients, or from client to clients
* it's not pyinstaller-friendly for now
* com errors are catch'able thru the promise

it's a proof of concept : WUY means **W**eb **U**ser **Y**nterface ...

## to test/run

Download [the zip from here](https://github.com/manatlan/wuy/archive/master.zip)

    $ pip3 install aiohttp
    $ python3 -u simple.py

## to use

Install the lib :

    $ pip3 install wuy

create a python file "web.py", and copy/paste this:

    import wuy
    wuy.start(app=True)

Run it, like this :

    python3 web.py

It will create a "web/index.html", the defaut front-end ;-)

Edit "web/index.html", like this :

    <script src="wuy.js"></script>
    <button onclick="wuy.myadd(42,13).then( alert )">test</button>

Edit "web.py", like this :

    import wuy

    @wuy.expose
    def myadd(a,b):
        return a+b

    wuy.start(app=(640,480))

and rerun your script :

    python3 web.py

and you can start to code

## but the future is ... bright ;-)

See examples :

* [an_app](https://github.com/manatlan/wuy/blob/master/an_app.py)
* [an_app2](https://github.com/manatlan/wuy/blob/master/an_app2.py)
* [a_server](https://github.com/manatlan/wuy/blob/master/a_server.py)

with **wuy.Window** for app (which open/manage a chrome window app)

with **wuy.Server** for classic http/ws servers

