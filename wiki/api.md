# api

## on Python/side

### app.Window

  app.Window(port=DEFAULT_PORT,log=True,**kwargs) : constructor

the constructor will run the GUI (and start the web/ws server).
* **port** : [int] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
* **log** : [boolean] (defaut True) display, or not, the log in the current console.
* **kwargs** : to initialise the instance with its own variables. They will be availables on client side (ex: _wuy.my_var_), and on python side.

  method **emit( event, args )**

will send an event from the server to the client

* **event** : [string] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
* **args** : [list] (defaut True) display, or not, the log in the current console.

  method **init()**

override this method to initialize your needs.

  method **exit()**

will exit the current instance



### app.Server

  app.Window(port=DEFAULT_PORT,log=True,**kwargs) : constructor

the constructor will start the web/ws server
* **port** : [int] (default 8080) define your port.
* **log** : [boolean] (defaut True) display, or not, the log in the current console.
* **kwargs** : to initialise the instance with its own variables. They will be availables on client side (ex: _wuy.my_var_), and on python side (_self.my_var_).

  method **emit( event, args )**

will send an event from the server to the client

* **event** : [string] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
* **args** : [list] (defaut True) display, or not, the log in the current console.

  method **init()**

override this method to initialize your needs.
