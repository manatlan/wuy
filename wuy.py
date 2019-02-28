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

__version__ = "0.10.0"

from aiohttp import web, WSCloseCode
from multidict import CIMultiDict
import concurrent
import aiohttp
import asyncio
import json, sys, os
import webbrowser
import traceback
import uuid
import inspect
import types
import base64
import socket
import tempfile
import subprocess
import platform
from urllib.parse import urlparse
import inspect
import re
from datetime import datetime, date


"""
cef troubles, to fix (before 1.0 release):
    - FIX: set title don't work on *nix (Issue #252)
    - FIX: chain'able broken (test app3)
    - EVOL: make contextual menu (dev tools) optional
    - TEST: freezing with cef
"""

DEFAULT_PORT = 8080

application = None
currents = {}  # NEW
isLog = None
FULLSCREEN = "fullscreen"  # const !
PATH = os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0])))

try:
    if not getattr(
        sys, "frozen", False
    ):  # bypass uvloop in frozen app (wait pyinstaller hook)
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

# helpers
#############################################################
def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((ip, int(port)))
        return True
    except socket.error as e:
        return False
    finally:
        s.close()


def serialize(obj):
    def toJSDate(d):
        assert type(d) in [datetime, date]
        d = datetime(d.year, d.month, d.day, 0, 0, 0, 0) if type(d) == date else d
        return d.isoformat() + "Z"

    if isinstance(obj, (datetime, date)):
        return toJSDate(obj)
    if isinstance(obj, bytes):
        return str(obj, "utf8")
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return str(obj)


def unserialize(obj):
    if type(obj) == str:
        if re.search("^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z$", obj):
            return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%fZ")
        elif re.search("^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$", obj):
            return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%SZ")
    elif type(obj) == list:
        return [unserialize(i) for i in obj]
    return obj


def jDumps(obj):
    return json.dumps(obj, default=serialize)


def jLoads(s):
    return unserialize(
        json.loads(s, object_pairs_hook=lambda obj: {k: unserialize(v) for k, v in obj})
    )


class JDict:
    def __init__(self, f: str):
        self.__f = os.path.join(PATH, f)
        try:
            with open(self.__f, "r+") as fid:
                self.__d = (
                    json.load(
                        fid,
                        object_pairs_hook=lambda obj: {
                            k: unserialize(v) for k, v in obj
                        },
                    )
                    or {}
                )
        except FileNotFoundError as e:
            self.__d = {}

    def set(self, k: str, v):
        self.__d[k] = v
        self.__save()

    def get(self, k: str = None):
        return self.__d.get(k, None) if k else self.__d

    def __save(self):
        with open(self.__f, "w+") as fid:
            json.dump(self.__d, fid, indent=4, sort_keys=True, default=serialize)


def path(f):
    if hasattr(sys, "_MEIPASS"):  # when freezed with pyinstaller ;-)
        return os.path.join(sys._MEIPASS, f)
    else:
        return os.path.join(PATH, f)


def wlog(*l):
    if isLog:
        s = " ".join([str(i) for i in l])
        if len(s) > 200:
            s = s[:200] + "..."
        print(s)


def find_chrome_win():
    import winreg  # TODO: pip3 install winreg

    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    for install_type in winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE:
        try:
            with winreg.OpenKey(install_type, reg_path, 0, winreg.KEY_READ) as reg_key:
                return winreg.QueryValue(reg_key, None)
        except WindowsError:
            pass


def find_chrome_mac():
    default_dir = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(default_dir):
        return default_dir


class ChromeApp:
    def __init__(self, url, size=None, chromeArgs=[]):
        self.__instance = None

        if sys.platform[:3] == "win":
            exe = find_chrome_win()
        elif sys.platform == "darwin":
            exe = find_chrome_mac()
        else:
            for i in ["chromium-browser", "chromium", "google-chrome", "chrome"]:
                try:
                    exe = webbrowser.get(i).name
                    break
                except webbrowser.Error:
                    exe = None

        if exe:
            args = [exe, "--app=" + url] + chromeArgs
            if size == FULLSCREEN:
                args.append("--start-fullscreen")
            if tempfile.gettempdir():
                args.append(
                    "--user-data-dir=%s"
                    % os.path.join(tempfile.gettempdir(), ".wuyapp")
                )
            # self.__instance = subprocess.Popen( args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL ) # make troubles on windows (freezd with noconsole don't start)
            self.__instance = subprocess.Popen(args)
        else:
            raise Exception("no browser")

    def wait(self):
        if self.__instance:
            return self.__instance.wait()

    def __del__(self):
        if self.__instance:
            self.__instance.kill()


###############################################################
## works with CefPython3
###############################################################
class ChromeAppCef:
    def __init__(self, url, size=None, chromeArgs=None):  # chromeArgs is not used
        import pkgutil

        assert pkgutil.find_loader("cefpython3"), "cefpython3 not available"

        def cefbrowser():
            from cefpython3 import cefpython as cef
            import ctypes

            isWin = platform.system() == "Windows"

            windowInfo = cef.WindowInfo()
            windowInfo.windowName = "CefPython3"
            if type(size) == tuple:
                w, h = size[0], size[1]
                windowInfo.SetAsChild(0, [0, 0, w, h])  # not win
            else:
                w, h = None, None

            sys.excepthook = cef.ExceptHook

            settings = {
                "product_version": "Wuy/%s" % __version__,
                "user_agent": "Wuy/%s (%s)" % (__version__, platform.system()),
                "context_menu": dict(
                    enabled=True,
                    navigation=False,
                    print=False,
                    view_source=False,
                    external_browser=False,
                    devtools=True,
                ),
            }
            cef.Initialize(settings, {})
            b = cef.CreateBrowserSync(windowInfo, url=url)

            if isWin and w and h:
                window_handle = b.GetOuterWindowHandle()
                SWP_NOMOVE = 0x0002  # X,Y ignored with SWP_NOMOVE flag
                ctypes.windll.user32.SetWindowPos(
                    window_handle, 0, 0, 0, w, h, SWP_NOMOVE
                )

            # ===---
            def wuyInit(width, height):
                if size == FULLSCREEN:
                    if isWin:
                        b.ToggleFullscreen()  # win only
                    else:
                        b.SetBounds(0, 0, width, height)  # not win

            bindings = cef.JavascriptBindings()
            bindings.SetFunction("wuyInit", wuyInit)
            b.SetJavascriptBindings(bindings)

            b.ExecuteJavascript("wuyInit(window.screen.width,window.screen.height)")
            # ===---

            class WuyClientHandler(object):
                def OnLoadEnd(self, browser, **_):
                    pass  # could serve in the future (?)

            class WuyDisplayHandler(object):
                def OnTitleChange(self, browser, title):
                    try:
                        cef.WindowUtils.SetTitle(browser, title)
                    except AttributeError:
                        print(
                            "**WARNING** : title changed '%s' not work on linux" % title
                        )

            b.SetClientHandler(WuyClientHandler())
            b.SetClientHandler(WuyDisplayHandler())

            cef.MessageLoop()
            cef.Shutdown()

        from threading import Thread

        t = Thread(target=cefbrowser)
        t.start()


###############################################################


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
jar = aiohttp.CookieJar(unsafe=True)


class Request:  # just to transform aiohttp.Request in wuy.Request (abstraction)
    def __init__(self, req):
        self.method = req.method
        self.path = req.path
        self.headers = req.headers
        self.query = req.rel_url.query
        self.body = None


class Response:
    def __init__(self, status, content, headers=None):
        self.status = status

        if headers is None:
            self.headers = CIMultiDict()
            if content is not None and type(content) == bytes:
                self.headers["Content-Type"] = "application/octet-stream"
            else:
                self.headers["Content-Type"] = "text/html"
        else:
            if type(headers) == str:
                self.headers = CIMultiDict([("Content-Type", headers)])
            else:
                self.headers = headers

        self.content = content


async def request(
    url, data=None, headers={}
):  # mimic urllib.Request() (GET & POST only)
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        try:
            if data:
                async with session.post(
                    url, data=data, headers=headers, ssl=False
                ) as resp:
                    return Response(
                        resp.status, await resp.text(), headers=resp.headers
                    )
            else:
                async with session.get(url, headers=headers, ssl=False) as resp:
                    return Response(
                        resp.status, await resp.text(), headers=resp.headers
                    )
        except aiohttp.client_exceptions.ClientConnectorError as e:
            return Response(None, str(e))


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


# Async aiohttp things (use current)
#############################################################
async def wsSend(ws, **kargs):
    if not ws.closed:
        wlog("< send:", kargs)
        await ws.send_str(jDumps(kargs))  # TODO: should remove ws from list ?


async def wsBroadcast(instance, event, args, exceptMe=None):
    for ws in instance._clients:
        if id(ws) != id(exceptMe):
            await wsSend(ws, event=event, args=args)


async def handleProxy(req):  # proxify "/_/<url>" with headers starting with "set-"
    url = req.match_info.get("url", None)
    if req.query_string:
        url = url + "?" + req.query_string
    headers = {k[4:]: v for k, v in req.headers.items() if k.lower().startswith("set-")}
    r = await request(
        url, data=req.can_read_body and (await req.text()), headers=headers
    )
    wlog(". serve proxy url", url, headers, ":", r.status)
    h = {"Server": "Wuy Proxified request (%s)" % __version__}
    for k, v in r.headers.items():
        if k.lower() in ["content-type", "date", "expires", "cache-control"]:
            h[k] = v
    return web.Response(status=r.status or 0, text=r.content, headers=h)


getname = lambda x: x.rsplit(".", 1)[0].replace("/", ".")


async def handleWeb(req):  # serve all statics from web folder
    ressource = req.match_info.get("path", "")
    if ressource == "" or ressource.endswith("/"):
        ressource += "index.html"
    if ressource.lower().endswith((".html", ".htm")):
        name = getname(ressource)
        if name in currents:
            html = currents[name]._render(path(os.path.dirname(ressource)))
            if html:  # the instance render its own html, go with it
                if re.findall(r"""<.*script.*src.*=.*['"]wuy.js['"].*>""", html):
                    return web.Response(status=200, body=html, content_type="text/html")
                else:
                    return web.Response(
                        status=200,
                        body='<script src="wuy.js"></script>\n' + html,
                        content_type="text/html",
                    )

    # classic serve static file or 404

    file = path(os.path.join("web", ressource))

    if os.path.isfile(file):
        wlog("- serve static file", file)
        return web.FileResponse(file)
    else:
        wreq = Request(req)
        if req.body_exists:  # override body
            wreq.body = await req.read()

        for name, instance in currents.items():
            ret = instance.request(wreq)
            if ret is not None:
                r = await ret if asyncio.iscoroutine(ret) else ret
                if r is not None:
                    if type(r) != Response:
                        r = Response(status=200, content=r)

                    wlog("- serve dynamic via", name, r)
                    return web.Response(
                        status=r.status, body=r.content, headers=r.headers
                    )

        wlog("! 404 on", file)
        return web.Response(status=404, body="file not found")


async def handleJs(req):  # serve the JS
    pp = urlparse(req.headers["Referer"]).path[
        1:
    ]  # TODO: what if browser hide its referer ????
    if pp.endswith("/") or pp == "":
        pp += "index.html"
    page = getname(pp)
    instance = currents[page]

    wlog(
        "- serve wuy.js to",
        page,
        instance._size and ("(with resize to " + str(instance._size) + ")") or "",
    )

    name = os.path.basename(sys.argv[0])
    if "." in name:
        name = name.split(".")[0]
    js = """
document.addEventListener("DOMContentLoaded", function(event) {
    %s
    %s
},true)

const dateFormat = /^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z$/;

function reviver(key, value) {
    if (typeof value === "string" && dateFormat.test(value)) {
        return new Date(value);
    }
    return value;
}

function setupWS( cbCnx ) {
    var url=window.location.origin.replace("http","ws")+"/_ws_%s"
    var ws=new WebSocket( url );

    ws.onmessage = function(evt) {
      var r = JSON.parse(evt.data, reviver );
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

var wuy={
    _ws: setupWS( function(ws){wuy._ws = ws; document.dispatchEvent( new CustomEvent("init") )} ),
    on: function( evt, callback ) {     // to register an event on a callback
        document.addEventListener(evt,function(e) { callback.apply(callback,e.detail) })
    },
    emit: function( evt, data) {        // to emit a event to all clients (except me), return a promise when done
        var args=Array.prototype.slice.call(arguments)
        return wuy._call("emit", args)
    },
    init: function( callback ) {
        function start() {
            document.removeEventListener("init", start)
            callback()
        }
        if(wuy._ws.readyState == wuy._ws.OPEN)
            start()
        else
            document.addEventListener("init", start)
    },
    _call: function( method, args ) {
        var cmd={
            command:    method,
            args:       args,
            uuid:       method+"-"+Math.random().toString(36).substring(2), // stamp the exchange, so the callback can be called back (thru customevent),
        };

        if(wuy._ws) {
            wuy._ws.send( JSON.stringify(cmd) );

            return new Promise( function (resolve, reject) {
                document.addEventListener('wuy-'+cmd.uuid, function handler(x) {
                    this.removeEventListener('wuy-'+cmd.uuid, handler);
                    var x=x.detail;
                    if(x && x.result!==undefined)
                        resolve(x.result)
                    else if(x && x.error!==undefined)
                        reject(x.error)
                });
            })
        }
        else
            return new Promise( function (resolve, reject) {
                reject("not connected");
            })
    },
    fetch: function(url,obj) {
        var h={"cache-control": "no-cache"};    // !!!
        if(obj && obj.headers)
            Object.keys(obj.headers).forEach( function(k) {
                h["set-"+k]=obj.headers[k];
            })
        var newObj = Object.assign({}, obj)
        newObj.headers=h;
        newObj.credentials= 'same-origin';
        return fetch( "/_/"+url,newObj )
    },
};
""" % (
        instance._size
        and "window.resizeTo(%s,%s);" % (instance._size[0], instance._size[1])
        or "",
        'if(!document.title) document.title="%s";' % name,
        page,
        instance._closeIfSocketClose
        and "window.close()"
        or "setTimeout( function() {setupWS(cbCnx)}, 1000);",
    )

    if instance._kwargs:
        for k, v in instance._kwargs.items():
            j64 = str(
                base64.b64encode(bytes(jDumps(v), "utf8")), "utf8"
            )  # thru b64 to avoid trouble with quotes or strangers chars
            js += """\nwuy.%s=JSON.parse(atob("%s"),reviver);""" % (k, j64)

    for k in instance._routes.keys():
        js += (
            """\nwuy.%s=function(_) {return wuy._call("%s", Array.prototype.slice.call(arguments) )};"""
            % (k, k)
        )

    return web.Response(status=200, text=js)


async def wshandle(req):
    global currents
    page = req.match_info["page"]
    if page not in currents:
        return None
    instance = currents[page]

    ws = web.WebSocketResponse()
    await ws.prepare(req)
    instance._clients.append(ws)
    wlog("Socket connected", page)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                try:
                    o = jLoads(msg.data)
                    wlog("> RECEPT", page, o)
                    if o["command"] == "emit":
                        event, *args = o["args"]
                        await wsBroadcast(
                            instance, event, args, ws
                        )  # emit to everybody except me
                        r = dict(
                            result=args
                        )  # but return the same content sended, thru the promise
                    else:
                        ret = instance._routes[o["command"]](*o["args"])
                        if ret and asyncio.iscoroutine(ret):
                            wlog(". ASync call", page, o["command"])

                            async def waitReturn(coroutine, uuid):
                                try:
                                    ret = await coroutine
                                    m = dict(result=ret, uuid=uuid)
                                except concurrent.futures._base.CancelledError as e:
                                    m = dict(error="task cancelled", uuid=uuid)
                                except Exception as e:
                                    m = dict(error=str(e), uuid=uuid)
                                    print("=" * 40, "in ASync", o["command"])
                                    print(traceback.format_exc().strip())
                                    print("=" * 40)
                                await wsSend(ws, **m)

                            asyncio.ensure_future(waitReturn(ret, o["uuid"]))
                            continue  # don't answer yet (the coroutine will do it)

                        r = dict(result=ret)
                except Exception as e:
                    r = dict(error=str(e))
                    print("=" * 40, "Exception on Recept", msg.data)
                    print(traceback.format_exc().strip())
                    print("=" * 79)

                if "uuid" in o:
                    r["uuid"] = o["uuid"]

                await wsSend(ws, **r)
            elif msg.type == web.WSMsgType.close or msg.tp == web.WSMsgType.error:
                break
    finally:
        wlog("Socket disconnected", page)
        instance._clients.remove(ws)

    if instance._closeIfSocketClose:
        _exit(instance)
    return ws


def _emit(instance, event, *args):  # sync version of emit for py side !
    asyncio.ensure_future(wsBroadcast(instance, event, args))


def _exit(instance=None):  # exit method
    global application

    if asyncio.get_event_loop().is_running():
        asyncio.get_event_loop().stop()

    if instance and hasattr(instance, "_browser") and instance._browser:
        del instance._browser
        instance._browser = None

    application = None
    wlog("exit")


async def on_shutdown(app):
    async def handle_exception(task):
        try:
            await task.cancel()
        except Exception:
            pass

    for task in asyncio.all_tasks():
        asyncio.ensure_future(handle_exception(task))


# WUY routines
#############################################################
class Base:
    _routes = {}
    _closeIfSocketClose = False
    _size = None
    _kwargs = {}  # Window/Server only

    def __init__(self, log=True):
        global isLog
        isLog = log

        self._name = self.__class__.__name__

        self._routes = {
            n: v
            for n, v in inspect.getmembers(self, inspect.ismethod)
            if not v.__func__.__qualname__.startswith(("Base.", "Window.", "Server."))
        }
        self._routes.update(
            dict(set=self.set, get=self.get)
        )  # add get/set config methods
        if "init" in self._routes:
            del self._routes[
                "init"
            ]  # ensure that a server-side init() is not exposed on client-side
        self._clients = []

    def _render(
        self, folder="."
    ):  # override this, if you want to do more complex things
        html = self.__doc__
        if html is None:
            # create startpage if not present and no docstring
            startpage = path(
                os.path.join(folder, "web", self.__class__.__name__ + ".html")
            )
            if not os.path.isfile(startpage):
                if not os.path.isdir(os.path.dirname(startpage)):
                    os.makedirs(os.path.dirname(startpage))
                with open(startpage, "w+") as fid:
                    fid.write("""<script src="wuy.js"></script>\n""")
                    fid.write("""Hello Wuy'rld ;-)""")
                print("Create '%s', just edit it" % startpage)
        return html

    @classmethod
    def _start(cls, host, port, instances, appmode):
        global application, currents

        for i in instances:
            i.init()
        currents = {i._name: i for i in instances}

        wlog(
            "Will accept : %s"
            % ["%s: %s" % (k, list(v._routes.keys())) for k, v in currents.items()]
        )  # TODO: not neat

        if application is None:

            application = web.Application()
            application.add_routes(
                [
                    web.get("/_ws_{page}", wshandle),
                    web.get("/{path:.*}wuy.js", handleJs),
                    web.get("/", handleWeb),
                    web.route("*", "/_/{url:.+}", handleProxy),
                    web.route("*", "/{path:.+}", handleWeb),
                ]
            )
            application.on_shutdown.append(on_shutdown)
            try:
                if (
                    appmode
                ):  # app-mode, don't shout "server started,  Running on, ctrl-c"
                    web.run_app(
                        application, host=host, port=port, print=lambda *a, **k: None
                    )
                else:
                    web.run_app(application, host=host, port=port)
            except concurrent.futures._base.CancelledError:
                pass  # die silently
            except RuntimeError:  # for tests stopping loop TODO check
                _exit()
            except KeyboardInterrupt:
                _exit()

            asyncio.set_event_loop(
                asyncio.new_event_loop()
            )  # renew, so multiple start are availables

    def emit(self, *a, **k):  # emit available for all
        _emit(self, *a, **k)

    def init(self):  # override this to make initializations
        pass

    def request(self, req):  # override to hook others web http requests
        pass

    def exit(self):  # available for ALL !!!
        _exit()

    def set(self, key, value, file="config.json"):
        c = JDict(file)
        c.set(key, value)

    def get(self, key=None, file="config.json"):
        c = JDict(file)
        return c.get(key)


class Window(Base):
    size = True  # or a tuple (wx,wy)
    _port = None
    chromeArgs = []

    def __init__(self, port=DEFAULT_PORT, log=True, **kwargs):
        super().__init__(log)
        self.__dict__.update(kwargs)
        self._kwargs = kwargs
        self._run(port=port)

    def _run(self, port):  # start method (app can be True, (width,height), ...)
        app = self.size

        self._closeIfSocketClose = True
        host = "localhost"
        if Window._port is None:
            while not isFree(host, port):
                port += 1
            Window._port = port
        else:
            port = Window._port

        url = "http://%s:%s/%s?%s" % (
            host,
            port,
            self._name + ".html",
            uuid.uuid4().hex,
        )

        if type(app) == tuple and len(app) == 2:  # it's a size tuple : set it !
            self._size = app

        try:
            # self._browser=ChromeAppCef(url,app)    # with CefPython3 !!!
            self._browser = ChromeApp(url, app, chromeArgs=self.chromeArgs)
        except Exception as e:
            print("Can't find Chrome on your desktop : %s" % e)
            sys.exit(-1)

        Base._start(host, port, [self], True)


class Server(Base):
    def __init__(self, port=DEFAULT_PORT, log=True, autorun=True, **kwargs):
        super().__init__(log)
        self.__dict__.update(kwargs)
        self._kwargs = kwargs
        if autorun:
            Base._start("0.0.0.0", port, [self], False)

    @classmethod
    def run(cls, port=DEFAULT_PORT, log=True, **kwargs):
        global isLog
        isLog = log
        allClasses = globals()[cls.__name__].__subclasses__()
        instances = [c(autorun=False, **kwargs) for c in allClasses]
        cls._start("0.0.0.0", port, instances, False)


if __name__ == "__main__":
    pass
