## Create an App/Window

In this tutorial : we will create a GUI which will provide a button whose will do a simple addition of two numbers (in python side).

Create a python file "web.py", and copy/paste this:

```python
import wuy

class index(wuy.Window):
    pass

index()
```
Run it, like this :

    $ python3 web.py

It will create a "web/index.html", the default front-end template ;-)

Edit "web/index.html", like this :

```html
<script src="wuy.js"></script>
<button onclick="wuy.myadd(42,13).then( alert )">test</button>
```

**Note**: When not using its "own rendering" (`__doc__` style or `_render() override`) ; it's up to you to include `<script src="wuy.js"></script>` (like in this example). When using "own rendering" : **wuy** insert it (at top) if not present.

Edit "web.py", like this :

```python
import wuy

class index(wuy.Window):
    size=(640,480)
    def myadd(self, a,b):
        return a+b

index()
```

and rerun your script :

    $ python3 web.py

and you can start to build your wonderful GUI ;-)

**TIP** : if you want the server mode (aka : use many clients from anywhere) ; just replace _wuy.Window_ by _wuy.Server_ !

[Learn More on differences between window & server modes](https://github.com/manatlan/wuy/blob/master/wiki/diff.md)
