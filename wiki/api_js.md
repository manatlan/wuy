# On Javascript Side

---
#### wuy.emit( event, args ) -> Promise
Will send an event from the client to others clients, except self.
  * **event** : [string] the name of the event
  * **args** : [list] a list of object

---
#### wuy.on( event, callback )
Subscribe to an event
  * **event** : [string] the name of the event
  * **callback** : a javascript method which handle params received by the event
  
---
#### wuy.<method>( <args> )
Call the serverside rpc method defined in your wuy.Window ou wuy.Server

By the way, you can access to the variables declared (kwargs) in the constructor of your wuy application.

If you have declared, in python side :

```python
class myApp(wuy.Window):
     pass
     
myApp( myVar=42 )
```
You can access it on js side:

```javascript
console.log( wuy.mYvar )
```


