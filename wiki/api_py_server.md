# wuy.Server
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
  * **event** : [string] the name of the event to send
  * **args** : [list] A list of arguments to send with the event

---
#### method init()
Override this method to initialize your needs.
