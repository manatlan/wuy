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
import base64


__version__="0.4.4"
DEFAULT_PORT=8080

application=None
current=None    # the current instance of Base

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

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
    if current and current._isLog: print(*a)

def getChrome():
    def getExe():
        if sys.platform in ['win32', 'win64']:
            return find_chrome_win()
        elif sys.platform == 'darwin':
            return find_chrome_mac()

    exe=getExe()
    if exe:
        return webbrowser.GenericBrowser(exe)
    else:
        webbrowser._tryorder=['google-chrome','chrome',"chromium","chromium-browser"]
        try:
            return webbrowser.get()
        except webbrowser.Error:
            return None

def find_chrome_win():
    import winreg #TODO: pip3 install winreg
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
    for install_type in winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE:
        try:
            with winreg.OpenKey(install_type, reg_path, 0, winreg.KEY_READ) as reg_key:
                return winreg.QueryValue(reg_key, None)
        except WindowsError:
            pass

def find_chrome_mac():
    default_dir = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.path.exists(default_dir):
        return default_dir

def openApp(url):
    chrome=getChrome()
    if chrome:
        if isinstance(chrome,webbrowser.GenericBrowser):
            chrome.args=["--app="+url]
            return chrome.open(url, new=1, autoraise=True)
        else:
            return chrome._invoke(["--app="+url],1,1)


# Async aiohttp things (use current)
#############################################################
async def wsSend( ws, **kargs ):
    log("< send:",kargs)
    await ws.send_str( json.dumps( kargs ) )


async def asEmit(event,args,exceptMe=None):
    global current
    for ws in current._clients:
        if id(ws) != id(exceptMe):
            await wsSend(ws,event=event, args=args )

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
        _ws: setupWS( function(ws){wuy._ws = ws} ),
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
        get: function(target, propKey, receiver){   // proxy: wuy.method(args) ---> wuy._call( method, args )
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
            j64=str(base64.b64encode(bytes(json.dumps(v),"utf8")),"utf8")   # thru b64 to avoid trouble with quotes or strangers chars
            js+="""\nwuy.%s=JSON.parse(atob("%s"));""" % (k,j64)

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
                    await asEmit( event, args, ws) # emit to everybody except me
                    r=dict(result = args)           # but return the same content sended, thru the promise
                else:
                    ret=current._routes[o["command"]]( *o["args"] )
                    if ret and asyncio.iscoroutine(ret):
                        log(". ASync call",o["command"])

                        async def waitReturn( coroutine,uuid ):
                            try:
                                ret=await coroutine
                                m=dict(result=ret, uuid=uuid)
                            except Exception as e:
                                m=dict(error=str(e), uuid=uuid)
                                print("="*40,"in ASync",o["command"])
                                print(traceback.format_exc().strip())
                                print("="*40)
                            await wsSend(ws, **m )

                        asyncio.ensure_future( waitReturn(ret,o["uuid"]) )
                        continue # don't answer yet (the coroutine will do it)

                    r=dict(result = ret )
            except Exception as e:
                r=dict(error = str(e))
                print("="*40,"on Recept",msg.data)
                print(traceback.format_exc().strip())
                print("="*79)

            if "uuid" in o: r["uuid"]=o["uuid"]

            await wsSend(ws, **r )
        elif msg.type == web.WSMsgType.close:
            break

    current._clients.remove( ws )
    if current._closeIfSocketClose: exit()
    return ws

def emit(event,args):   # sync version of emit for py side !
    asyncio.ensure_future( asEmit( event, args) )

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
        global current,application

        try:
            os.chdir(os.path.split(sys.argv[0])[0])
        except:
            pass

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
            url = "http://localhost:%s/%s?%s"% (port,page,uuid.uuid4().hex)
            isBrowser = openApp(url)
            if isBrowser:
                self._closeIfSocketClose=True
            else:
                print("Can't find Chrome on your desktop ;-(")
                print("(Switch to server mode)")
                print("Surf to %s !" % url)

            if type(app)==tuple and len(app)==2:    #it's a size tuple : set it !
                self._size=app

        self.init()

        if application is None:
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

    def init(self):
        pass

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
    openApp("https://github.com/manatlan/wuy")
