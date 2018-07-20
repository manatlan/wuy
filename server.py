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

clients=[]

async def as_emit(event,args,exceptMe=None):
    global clients
    for ws in clients:
        if id(ws) != id(exceptMe):
            print("emit '%s' : %s" % (event,args))
            await ws.send_str( json.dumps( dict(event=event,args=args) ))

def emit(event,args):
    asyncio.ensure_future( as_emit( event, args) )

async def handle(request):
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
                    await as_emit( event, args, ws)
                    r=dict(result = args)
                else:
                    pythonMethod = getattr(sys.modules[__name__], o["command"])
                    r=dict(result = pythonMethod( *o["args"] ) )
            except Exception as e:
                r=dict(error = str(e))

            if "uuid" in o: r["uuid"]=o["uuid"]

            print("sent",r)
            await ws.send_str( json.dumps( r ) )
        elif msg.type == web.WSMsgType.close:
            break

    clients.remove( ws )

    return ws

################################################# exposed methods vv

def my_python_method(a,b):
    return a+b

def my_python_method2(a):
    emit( "js_event", "from python sync")
    return a*2

async def handleTest(request):
    await as_emit( "js_event", "from python async")
    return web.Response(body="ok")

if __name__=="__main__":
    app = web.Application()
    app.add_routes([
            web.get('/ws', wshandle),

            web.get('/test', handleTest),

            web.get('/', handle),
            web.get('/{path}', handle),
    ])
    web.run_app(app)
