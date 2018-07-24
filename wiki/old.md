## Create a wuy app, in the old/eel style

**warning** : It's not recommended, it's deprecated, and just here to show that's like eel ... [You should start with the new style] !(https://github.com/manatlan/wuy/blob/master/wiki/tuto.md)

Create a python file "web.py", and copy/paste this:

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

It's really like [python eel](https://github.com/ChrisKnott/Eel), but [you should start with the new style] (https://github.com/manatlan/wuy/blob/master/wiki/tuto.md) if you want to go with **wuy**.

If you want to migrate from eel to wuy :

* Pay attention on calling rpc methods : _eel.myadd(42,13)( alert _) -> _wuy.myadd(42,13).then( alert )_ (wuy use classic promises (catch'able))
* On py side : replace _eel_ by _wuy_.
* On js side : you can't expose JS method to python : you should use the pubsub mechanism (JS: _wuy.on("event",callback)_ / PY: _wuy.emit("event", *args)_ ). (Keep in mind ; that in server mode : you can have multiple clients, so calling a js from py side is a non-sense).
* On js side : rename _eel.js_ -> _wuy.js_