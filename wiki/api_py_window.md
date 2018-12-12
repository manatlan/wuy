# wuy.Window
To let your wuy application act as a GUI in mode app/window.

---
#### wuy.Window(port=DEFAULT_PORT, log=True, ** kwargs) : constructor
The constructor will run the GUI (and start the web/ws server).
  * **port** : [int] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
  * **log** : [boolean] (defaut True) display, or not, the log in the current console.
  * **kwargs** : to initialise the instance with its own variables. They will be availables on client side (ex: _wuy.my_var_), and on python side.

---
#### method emit( event, args )
Will send an event from the server to the client
  * **event** : [string] the name of the event to send
  * **args** : [list] A list of arguments to send with the event

---
#### method init()
Override this method to initialize your needs.

---
#### method exit()
Will exit the current instance

---
#### set( key, value, file='config.json' )
Will store the `value` (object) for the `key`(string), in the default `file` (config.json).

---
#### get( key=None, file='config.json' ) -> value
Will get the value of the `key`, from the default `file` (config.json). If the `key` is unknown, it returns `None`.
(If the `key` is None ; it will return all that is stored in the default `file` (config.json))

---
#### attribut size
Set the size of the window. size can be a tuple (width,height) or None

---
#### attribut chromeArgs
Here you can add default arguments to the chrome instance. By default, it's an empty list.
example : `chromeArgs = ["--no-proxy-server"]`

---
Like the other mode ; just inherit of this class and declare your rpc method (sync or async style), to let them available in the js side.



