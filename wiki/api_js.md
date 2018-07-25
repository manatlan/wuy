# On Javascript Side

#### wuy.emit( event, args ) -> Promise
Will send an event from the client to others clients, except self.
  * **event** : [string] the name of the event
  * **args** : [list] a list of object

#### wuy.on( event, callback )
Subscribe to an event
  * **event** : [string] the name of the event
  * **callback** : a javascript method which handle params received by the event
  
#### wuy.<method>( <args> )
Call the serverside rpc method defined in your wuy.Window ou wuy.Server

