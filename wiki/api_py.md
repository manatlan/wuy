# api on Python Side

### wuy.Window
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
  * **event** : [string] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
  * **args** : [list] (defaut True) display, or not, the log in the current console.

---
#### method init()
Override this method to initialize your needs.

---
#### method exit()
Will exit the current instance

---
#### attribut size
Set the size of the window. size can be a tuple (width,height) or None




### wuy.Server
To let your wuy application act as a regular web server

---
#### wuy.Window(port=DEFAULT_PORT, log=True, ** kwargs) : constructor
The constructor will start the web/ws server
  * **port** : [int] (default 8080) define your port.
  * **log** : [boolean] (defaut True) display, or not, the log in the current console.
  * **kwargs** : to initialise the instance with its own variables. They will be availables on client side (ex: _wuy.my_var_), and on python side (_self.my_var_).

---
#### method emit( event, args )
Will send an event from the server to the client
  * **event** : [string] (default 8080) define your port, but if it's already in use : **wuy** will try the next free port to run the server part.
  * **args** : [list] (defaut True) display, or not, the log in the current console.

---
#### method init()
Override this method to initialize your needs.
