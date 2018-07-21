# -*- coding: utf-8 -*-
import huy

@huy.expose
def my_python_method(a,b):
    return a+b

@huy.expose
def my_python_method2(a):
    huy.emit( "js_event", "from python sync")   # emit an event to all clients (me too !)
    return a*2

@huy.expose
def my_python_exit():
    huy.exit()

if __name__=="__main__":
    huy.start(app=True) # run a browser & close when no socket
    # huy.start(app=False) # (default) run as a normal http/ws server
