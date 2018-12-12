# On Javascript Side

---
#### wuy.emit( event, arg1, arg2, ... ) -> Promise
Will send an event from the client to others clients, except self. It returns a Promise which resolve (with the params of the event) if the event as been sent to others. Otherwise, it rejects with the error.
  * **event** : [string] the name of the event
  * **args** : arguments sent with the event

---
#### wuy.on( event, callback )
Subscribe to an event.
  * **event** : [string] the name of the event
  * **callback** : a javascript method which handle params received by the event

---
#### wuy.fetch( url, obj ) -> Promise
Exactly as window.fetch(), but proxified thru serverside ([learn more](https://github.com/manatlan/wuy/blob/master/wiki/proxify.md))

---
#### wuy.set( key, value, file='config.json' ) -> Promise
Will store the `value` (object) for the `key`(string), in the default `file` (config.json), on server side.

---
#### wuy.get( key=null, file='config.json' ) -> Promise
Will get the value of the `key`, from the default `file` (config.json), from server side. If the `key` is unknown, the promise resolves `null`.
(If the `key` is null ; it will return all that is stored in the default `file` (config.json), from server side)

---
#### wuy.--method--( arg1, arg2, ... ) -> Promise
Call the serverside rpc method defined in your wuy.Window or wuy.Server. Otherwise, it rejects with the error.

---
#### wuy.init( callback )
The safe way to start your app that ensure all is loaded, and the
socket is connected. It calls the `callback` when it's done !

---
By the way, you can access to the variables declared (kwargs) in the constructor of your wuy application.

If you have declared, in python side :

```python
class myApp(wuy.Window):
     pass
     
myApp( myVar=42 )
```
You can access it on js side:

```javascript
console.log( wuy.myVar === 42 ) // it's true
```


