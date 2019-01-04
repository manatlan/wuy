# wuy 

If you have made a _super python tool_, and you want to add a GUI but without using qt/gtk/tk/wx/kivy/toga : you are in the right place ! Just re-use the local browser (chrome in app mode) as GUI, drived by **wuy**.

<p align="center">
    <img src="https://github.com/manatlan/wuy/blob/master/wiki/capture.png"/><br/>
    <a href="https://github.com/manatlan/wuy/blob/master/web/askName.html">html</a> / 
    <a href="https://github.com/manatlan/wuy/blob/master/an_app2.py">python</a>
</p>

Basically, it's a python module which will act as a web server (http & websocket) and will open/manage a window for you ; providing a simple framework (js/py3 helpers).

It lets you create your GUI with yours web skills (html/js/css or any js frameworks/libs), and re-use the power of python on server side.

Technically, it's a python3 module, using asyncio and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/), and (if present) the [uvloop](https://magic.io/blog/uvloop-blazing-fast-python-networking/), for the full speed ! The http server is here to serve static content (html, js, images ...). The websocket is here to simplify the communication (sync/async) between the window & the server. (rpc method to communicate from client to server, pubsub mechanism to communicate from server to clients, or from client to clients)

In **app/window mode** : it will manage (open/close) the window for you ; using the **chrome app mode** ; if the websocket brokes : window & server will shutdown (close the window ; the server will shutdown, close the server ; the window will shutdown). You (or your clients) will not see a difference with classical GUI !

In **server mode** : it will act as a classical web server ; and you can use as many clients/browsers as you want, from localhost or from anywhere else. Closing a socket ; just close the socket ;-). It can be hosted on the web, as long as the provider service use python3.

[More on window/server differences](https://github.com/manatlan/wuy/blob/master/wiki/diff.md)

In all cases : it will be pretty easy to produce/freeze an executable (windows/linux/apple) (one file with all html/js embedded), using [pyinstaller/windows](https://github.com/manatlan/wuy/blob/master/BUILD.bat). And share your _super python tool_ to the world (wuy comes with [its own freezer (a wuy app !)](https://github.com/manatlan/wuy/tree/master/examples/wuy_freezer))! And in the future : android !

Since 0.6; **wuy** provide a js method to [proxify http requests](https://github.com/manatlan/wuy/blob/master/wiki/proxify.md), to avoid CORS troubles.

Since 0.9; **wuy** provide get/set methods on client/server side to store/retrieve key/value pairs in a json file on serverside.

It's, a little bit, the same thing as [python eel](https://github.com/ChrisKnott/Eel).



**TODOs**:
* In the future : [cefpython3](https://github.com/cztomczak/cefpython) will be the platform of choice for running **wuy** apps on **android**/iphone (when [cef](https://bitbucket.org/chromiumembedded/cef/issues/1991/add-android-support) and [cefpython3](https://github.com/kivy-garden/garden.cefpython/issues/8) will be ready). Currently **wuy** works with cefpython3, on linux/windows/apple. It's working in the [unittests suite](https://github.com/manatlan/wuy/blob/master/wuy_tests.py) (you can already try ; modify _wuy.py_, replace ChromeApp() by ChromeAppCef())
* Write docs & examples

## The simplest example
This is _the hello world_ of **wuy**

```python
import wuy

class helloWorld(wuy.Window):
    """ <button onclick="wuy.beep()">BEEP</button> """
    size=(100,100)

    def beep(self):
        print("\a BEEP !!!")

helloWorld()
```

## To Test/Run

Download [the zip from here](https://github.com/manatlan/wuy/archive/master.zip)

    $ pip3 install aiohttp winreg
    $ python3 -u an_app.py

(_winreg_ is needed for windows only)

It's an app !

For a regular server example (many clients from anywhere on web)

    $ python3 -u a_server.py

## To Use

Install the lib :

    $ pip3 install wuy winreg

(_winreg_ is needed for windows only)

**And follow the [official tuto](https://github.com/manatlan/wuy/blob/master/wiki/README.md)**.


## See Examples

* [an_app](https://github.com/manatlan/wuy/blob/master/an_app.py) : all kind of tricks
* [an_app2](https://github.com/manatlan/wuy/blob/master/an_app2.py) : an input box
* [an_app3](https://github.com/manatlan/wuy/blob/master/an_app3.py) : an alert box with autodeclared js vars (chain'able windows)!
* [an_app4](https://github.com/manatlan/wuy/blob/master/an_app4.py) : using sync & async rpc calls !
* [an_app5](https://github.com/manatlan/wuy/blob/master/an_app5.py) : using async aiohttp.get (request content from web) & FULLSCREEN mode
* [an_app6](https://github.com/manatlan/wuy/blob/master/an_app6.py) : progress bars (async)
* [an_app7](https://github.com/manatlan/wuy/blob/master/an_app7.py) : html is inside the docstring ! (**SIMPLEST**)
* [an_app8](https://github.com/manatlan/wuy/blob/master/an_app8.py) : just to show how to organize your code when app's expand.
* [an_appVuejs](https://github.com/manatlan/wuy/blob/master/an_appVuejs.py) : using a vuejs app (and  a continuous push from server to client)
* [a_server](https://github.com/manatlan/wuy/blob/master/a_server.py) : a server, tchat service for multiple clients

Don't forget to have a look at [real examples](https://github.com/manatlan/wuy/tree/master/examples) too (real apps for real life)

A big real life app : See [jBrout3](https://github.com/manatlan/jbrout3) (in development), it's the rebirth of the good old py2/gtk app : [jBrout2](https://jbrout.manatlan.com). It use vuejs/vuex for front, and the jbrout's lib to manage photos.


## Doc

Use [wuy.Window](https://github.com/manatlan/wuy/blob/master/wiki/api_py_window.md) for app (which open/manage a chrome window app)

Use [wuy.Server](https://github.com/manatlan/wuy/blob/master/wiki/api_py_server.md) for classic http/ws servers

And client side (javascript), in all cases : use [wuy.js](https://github.com/manatlan/wuy/blob/master/wiki/api_js.md)

[Learn More on differences between this two class](https://github.com/manatlan/wuy/blob/master/wiki/diff.md)
