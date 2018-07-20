
document.addEventListener("DOMContentLoaded", function(event) {
})

function setupWS() {

    var ws=new WebSocket( window.location.origin.replace("http","ws")+"/ws" );

    ws.onmessage = function(evt) {
      var r = JSON.parse(evt.data);
      if(r.uuid) // that's a response from call py !
          document.dispatchEvent( new CustomEvent('evt-'+r.uuid,{ detail: r} ) );
      else if(r.event){ // that's an event from anywhere !
          document.dispatchEvent( new CustomEvent(r.event,{ detail: r.args } ) );
      }
    };

    ws.onclose = function(evt) {
        console.log("disconnected");
        huy._ws = null;
        setTimeout( setupWS, 1000);
    };
    ws.onerror = function(evt) {};
    ws.onopen=function(evt) {
        console.log("Connected",evt)
        huy._ws = ws;
    }

    return ws;
}

var huy = new Proxy( {
        _ws: setupWS(),
        on: function( evt, callback ) {
            document.addEventListener(evt,function(e) { callback(e.detail) })
        },
        emit: function( evt, data) {
            return huy.call("emit",evt,data)
        },
        call: function( _ ) {
            var args=Array.prototype.slice.call(arguments);

            var cmd={
                command:    args.shift(0),
                args:       args,
            };
            cmd.uuid = cmd.command+"-"+Math.random().toString(36).substring(2);
            huy._ws.send( JSON.stringify(cmd) );

            return new Promise( function (resolve, reject) {
                document.addEventListener('evt-'+cmd.uuid, function handler(x) {
                    this.removeEventListener('evt-'+cmd.uuid, handler);
                    var x=x.detail;
                    if(x && x.result)
                        resolve(x.result)
                    else
                        reject(x.error)
                });
            })

        }
    },
    {
        get: function(target, propKey, receiver){   // huy.method(args) ==> huy.call( method, args )
            if(target.hasOwnProperty(propKey))
                return target[propKey];
            else
                return function() {
                    var args=[propKey].concat( Array.prototype.slice.call(arguments) )
                    return target.call.apply( target, args);
                }
        }
    },
);




