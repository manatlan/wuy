# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018 manatlan manatlan[at]gmail(dot)com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# https://github.com/manatlan/wuy
# #############################################################################

from aiohttp import web
import asyncio
import json,sys,os
import webbrowser
import traceback
import uuid
import inspect
import types

__version__="0.3.4"
DEFAULT_PORT=8080

current=None    # the current instance of Base

# helpers
#############################################################
exposed={}
def expose( f ):    # decorator !
    global exposed
    exposed[f.__name__]=f
    return f

def path(f):
    if hasattr(sys,"_MEIPASS"): # when freezed with pyinstaller ;-)
        return os.path.join(sys._MEIPASS,f)  
    else:
        return f

def log(*a):
    if current._isLog: print(*a)

def getBrowser():
    for b in ['google-chrome','chrome',"chromium","chromium-browser","mozilla","firefox"]:
        try:
            return webbrowser.get(b)
        except webbrowser.Error:
            pass

def startApp(url):
    b=getBrowser()
    if b:
        if "mozilla" in str(b).lower():
            b._invoke(["--new-window",url],0,0) #window.close() won't work ;-(
        else:
            b._invoke(["--app="+url],1,1)
        return True



# Async aiohttp things (use current)
#############################################################
async def as_emit(event,args,exceptMe=None):
    global current
    for ws in current._clients:
        if id(ws) != id(exceptMe):
            log("  < emit event '%s' : %s" % (event,args))
            await ws.send_str( json.dumps( dict(event=event,args=args) ))

def emit(event,args):   # sync version of emit for py side !
    asyncio.ensure_future( as_emit( event, args) )

async def handleWeb(request): # serve all statics from web folder
    file = path('./web/'+request.match_info.get('path', "index.html"))
    if os.path.isfile(file):
        log("- serve static file",file)
        return web.FileResponse(file)
    else:
        log("! 404 on",file)
        return web.Response(status=404,body="file not found")

async def handleJs(request): # serve the JS
    log("- serve wuy.js",current._size and ("(with resize to "+str(current._size)+")") or "")

    name=os.path.basename(sys.argv[0])
    if "." in name: name=name.split(".")[0]
    js="""
document.addEventListener("DOMContentLoaded", function(event) {
    %s
    %s
},true)

function setupWS( cbCnx ) {

    var ws=new WebSocket( window.location.origin.replace("http","ws")+"/ws" );

    ws.onmessage = function(evt) {
      var r = JSON.parse(evt.data);
      if(r.uuid) // that's a response from call py !
          document.dispatchEvent( new CustomEvent('wuy-'+r.uuid,{ detail: r} ) );
      else if(r.event){ // that's an event from anywhere !
          document.dispatchEvent( new CustomEvent(r.event,{ detail: r.args } ) );
      }
    };

    ws.onclose = function(evt) {
        console.log("disconnected");
        cbCnx(null);
        %s
    };
    ws.onerror = function(evt) {cbCnx(null);};
    ws.onopen=function(evt) {
        console.log("Connected",evt)
        cbCnx(ws);
    }

    return ws;
}

var wuy = new Proxy( {
        _ws: setupWS( ws=>{wuy._ws = ws} ),
        on: function( evt, callback ) {     // to register an event on a callback
            document.addEventListener(evt,function(e) { callback(e.detail) })
        },
        emit: function( evt, data) {        // to emit a event to all clients (except me), return a promise when done
            return wuy._call("emit",evt,data)
        },
        _call: function( _ ) {               
            var args=Array.prototype.slice.call(arguments);

            var cmd={
                command:    args.shift(0),
                args:       args,
            };
            cmd.uuid = cmd.command+"-"+Math.random().toString(36).substring(2); // stamp the exchange, so the callback can be called back (thru customevent)
            if(wuy._ws) {
                wuy._ws.send( JSON.stringify(cmd) );

                return new Promise( function (resolve, reject) {
                    document.addEventListener('wuy-'+cmd.uuid, function handler(x) {
                        this.removeEventListener('wuy-'+cmd.uuid, handler);
                        var x=x.detail;
                        if(x && x.result)
                            resolve(x.result)
                        else
                            reject(x.error)
                    });
                })
            }
            else 
                return new Promise( function (resolve, reject) {
                    reject("not connected");
                })

        }
    },
    {
        get: function(target, propKey, receiver){   // proxy: wuy.method(args) ==> wuy._call( method, args )
            if(target.hasOwnProperty(propKey))
                return target[propKey];
            else
                return function() {
                    var args=[propKey].concat( Array.prototype.slice.call(arguments) )
                    return target._call.apply( target, args);
                }
        }
    },
);
""" % (
        current._size and "window.resizeTo(%s,%s);"%(current._size[0],current._size[1]) or "",
        'document.title="%s";'%name,
        current._closeIfSocketClose and "window.close()" or "setTimeout( function() {setupWS(cbCnx)}, 1000);"
        

    )


    if current._kwargs:
        for k,v in current._kwargs.items():
            js+="""\n%s=JSON.parse(`%s`);""" % (k,json.dumps(v))
    return web.Response(status=200,text=js)

async def wshandle(request):
    global current
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    current._clients.append(ws)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            try:
                o=json.loads( msg.data )
                log("> RECEPT",o)
                if o["command"] == "emit":
                    event, *args = o["args"]
                    await as_emit( event, args, ws) # emit to everybody except me
                    r=dict(result = args)           # but return the same content sended, thru the promise
                else:
                    ret=current._routes[ o["command"]]( *o["args"] )
                    if "coroutine" in str(type(ret)):
                        ret=await ret
                    r=dict(result = ret )
            except Exception as e:
                r=dict(error = str(e)) 
                print("="*79)
                print(traceback.format_exc())
                print("="*79)

            if "uuid" in o: r["uuid"]=o["uuid"]

            log("< return",r)
            await ws.send_str( json.dumps( r ) )
        elif msg.type == web.WSMsgType.close:
            break

    current._clients.remove( ws )
    if current._closeIfSocketClose: exit()
    return ws

def exit():         # exit method
    async def handle_exception(task):
        try:
            await task.cancel()
        except Exception:
            pass

    for task in asyncio.Task.all_tasks():
        asyncio.ensure_future(handle_exception(task))

    asyncio.get_event_loop().stop()
    asyncio.set_event_loop(asyncio.new_event_loop())    # renew, so multiple start are availables

    log("exit")

# WUY routines
#############################################################
class Base:
    _routes={}
    _clients=[]
    _closeIfSocketClose=False
    _isLog=False
    _size=None
    _kwargs={}  # Window/Server only
    def __init__(self,instance,exposed={}):
        if isinstance(instance,Base):
            self._name=instance.__class__.__name__
            self._routes={n:v for n, v in inspect.getmembers(instance, inspect.ismethod) if isinstance(v,types.MethodType) and "bound method %s."%self._name in str(v)}  #  TODO: there should be a better way to discover class methos
        else: # old style (eel)
            self._name=instance # aka page name
            self._routes=exposed

    def _run(self,port=DEFAULT_PORT,app=None,log=True):   # start method (app can be True, (width,size), ...)

        try:
            os.chdir(os.path.split(sys.argv[0])[0])
        except:
            pass

        global current
        current=self    # set current !

        self._isLog=log

        globals()["log"]("Will accept : %s" % ", ".join(self._routes.keys()) )  #TODO: not neat

        page=self._name+".html"

        # create startpage if not present
        startpage=path("./web/"+page)
        if not os.path.isfile(startpage):
            if not os.path.isdir(os.path.dirname(startpage)):
                os.makedirs(os.path.dirname(startpage))
            with open(startpage,"w+") as fid:
                fid.write('''<script src="wuy.js"></script>\n''')
                fid.write('''Hello Wuy'rld ;-)''')
            print("Create 'web/%s', just edit it" % os.path.basename(startpage))

        if app:
            self._closeIfSocketClose=startApp("http://localhost:%s/%s?%s"% (port,page,uuid.uuid4().hex))
            if type(app)==tuple and len(app)==2:
                self._size=app

        application=web.Application( loop=asyncio.get_event_loop() )
        application.add_routes([
            web.get('/ws',      wshandle),
            web.get('/wuy.js',  handleJs),
            web.get('/',        handleWeb),
            web.get('/{path}',  handleWeb),
        ])
        try:
            web.run_app(application,port=port)
        except KeyboardInterrupt:
            exit()

    def emit(self,*a,**k):  # emit available for all
        emit(*a,**k)


class Window(Base):
    size=True   # or a tuple (wx,wy)
    def __init__(self,port=DEFAULT_PORT,log=True,**kwargs):
        super().__init__(self)
        self.__dict__.update(kwargs)
        self._kwargs=kwargs
        self._run(app=self.size,port=port,log=log)

    def exit(self): # exit is available for Window !!
        exit()

class Server(Base):
    def __init__(self,port=DEFAULT_PORT,log=True,**kwargs):
        super().__init__(self)
        self.__dict__.update(kwargs)
        self._kwargs=kwargs
        self._run(app=False,port=port,log=log)


def start(page="index",port=DEFAULT_PORT,app=None,log=True):
    """ old style run with exposed methods (like eel) 
            'app' can be True, (width,size) (for window-like(app))            
            'app' can be None, False (for server-like)
    """
    b=Base(page,exposed)
    b._run(port=port,app=app,log=log)


if __name__=="__main__":
    log("test",42)
