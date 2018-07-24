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

and you can start to code
