# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import json,sys,os
import webbrowser

try:
    os.chdir(sys._MEIPASS)  # when freezed with pyinstaller ;-)
except:
    try:
        os.chdir(os.path.split(sys.argv[0])[0])
    except:
        pass

clients=[] #<- for saving clients cnx
exposed={} #<- for saving exposed methods
application = web.Application()
closeIfNoSocket=False

async def as_emit(event,args,exceptMe=None):
    global clients
    for ws in clients:
        if id(ws) != id(exceptMe):
            print("emit event '%s' : %s" % (event,args))
            await ws.send_str( json.dumps( dict(event=event,args=args) ))

def emit(event,args):   # sync version of emit for py side !
    asyncio.ensure_future( as_emit( event, args) )

async def handle(request): # serve all statics from web folder
    file = './web/'+request.match_info.get('path', "index.html")
    if os.path.isfile(file):
        return web.FileResponse(file)
    else:
        return web.Response(status=404,body="file not found")

async def wshandle(request):
    global clients

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    clients.append(ws)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            try:
                o=json.loads( msg.data )
                print("RECEPT",o)
                if o["command"] == "emit":
                    event, *args = o["args"]
                    await as_emit( event, args, ws) # emit to everybody except me
                    r=dict(result = args)           # but return the same content sended, thru the promise
                else:
                    r=dict(result = exposed[o["command"]]( *o["args"] ) )
            except Exception as e:
                r=dict(error = str(e))

            if "uuid" in o: r["uuid"]=o["uuid"]

            print("sent",r)
            await ws.send_str( json.dumps( r ) )
        elif msg.type == web.WSMsgType.close:
            break

    clients.remove( ws )
    if closeIfNoSocket and len(clients)==0: exit()
    return ws


def getBro():
    for b in ['google-chrome','chrome',"chromium","chromium-browser"]:
        try:
            i = webbrowser.get(b)
        except webbrowser.Error:
            i=None

        if i: return i

def open(url):
    b=getBro()
    if b:
        b._invoke(["--app="+url],1,1)
        return True


################################################# exposed methods vv
def expose( f ):    # decorator !
    global exposed
    exposed[f.__name__]=f
    return f

def exit():         # exit method
    application.loop.stop()
    sys.exit()

def start(port=8080,app=False):   # start method
    global closeIfNoSocket

    if app:
        closeIfNoSocket=open("http://localhost:%s"%port)

    application.add_routes([
            web.get('/ws', wshandle),

            web.get('/', handle),
            web.get('/{path}', handle),
    ])
    web.run_app(application,port=port)

if __name__=="__main__":
    pass
