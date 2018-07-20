#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import huy

@huy.expose
def my_python_method(a,b):
    return a+b

@huy.expose
def my_python_method2(a):
    huy.emit( "js_event", "from python sync")   # emit an event to all clients (me too !)
    return a*2

if __name__=="__main__":
    huy.start()
