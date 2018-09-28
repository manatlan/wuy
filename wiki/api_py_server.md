# wuy.Server
To let your wuy application act as a regular web server

---
#### wuy.Server(port=DEFAULT_PORT, log=True, ** kwargs) : constructor
The constructor will start the web/ws server
  * **port** : [int] (default 8080) define your port.
  * **log** : [boolean] (defaut True) display, or not, the log in the current console.
  * **kwargs** : to initialise the instance with its own variables. They will be availables on client side (ex: _wuy.my_var_), and on python side (_self.my_var_).

---
#### method emit( event, arg1, arg2, ... )
Will send an event from the server to the client
  * **event** : [string] the name of the event to send
  * **args** : arguments to send with the event

---
#### method init()
Override this method to initialize your needs.

---
#### method exit()
Will exit the server instance

---
#### set( key, value, file='config.json' )
Will store the `value` (object) for the `key`(string), in the default `file` (config.json).

---
#### get( key=None, file='config.json' ) -> value
Will get the value of the `key`, from the default `file` (config.json). If the `key` is unknown, it returns `None`.
(If the `key` is None ; it will return all that is stored in the default `file` (config.json))

---
#### classmethod run(port=DEFAULT_PORT, log=True, ** kwargs)
Will detect automatically all `wuy.Server` inheritances, and will run them together. Same args as the constructor ;-)

Here is an example:

```python
import wuy

class m1(wuy.Server):    # page m1 interact with this class
    def post(self,txt):
        self.emit( "addTxt", "1:"+txt)   # emit an event to all clients (me too !)

class m2(wuy.Server):    # page m2 interact with this class
    def post(self,txt):
        self.emit( "addTxt", "2:"+txt)   # emit an event to all clients (me too !)

if __name__=="__main__":
    wuy.Server.run()
```

---
Like the other mode ; just inherit of this class and declare your rpc method (sync or async style), to let them available in the js side.
