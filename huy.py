# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import json,sys,os

try:
    os.chdir(sys._MEIPASS)  # when freezed with pyinstaller ;-)
except:
    try:
        os.chdir(os.path.split(sys.argv[0])[0])
    except:
        pass

clients=[] #<- for saving clients cnx
exposed={} #<- for saving exposed methods
app = web.Application()

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
    # if len(clients)==0: app.loop.stop()
    return ws

################################################# exposed methods vv
def expose( f ):
    global exposed
    exposed[f.__name__]=f
    return f

def start(port=8080):
    app.add_routes([
            web.get('/ws', wshandle),

            web.get('/', handle),
            web.get('/{path}', handle),
    ])
    web.run_app(app,port=port)

if __name__=="__main__":
    pass
