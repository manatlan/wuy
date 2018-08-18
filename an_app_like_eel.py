# -*- coding: utf-8 -*-
import wuy

# like eel (old fashion way, using decorators)
# **DEPRECATED**

@wuy.expose
def my_python_method(a,b):
    return a+b

@wuy.expose
def my_python_method2(a):
    wuy.emit( "js_event", "from python sync")   # emit an event to all clients (me too !)
    return a*2

@wuy.expose
def my_python_exit():
    wuy.exit()

if __name__=="__main__":
    wuy.start(app=(400,200))    # run a browser & close when no socket & set size of the window
    # wuy.start(app=True)       # run a browser & close when no socket (get back the last size)
    # wuy.start()               # (default) run as a normal http/ws server (don't run a browser)
