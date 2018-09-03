# -*- coding: utf-8 -*-
import wuy


class index(wuy.Window):    # name the class as the web/<class_name>.html
    size=(300,300)

    def my_python_method(self,a,b):
        return a+b

    def my_python_method2(self,a):
        self.emit( "js_event", "from python sync")   # emit an event to all clients (me too !)
        return a*2

    def my_python_exit(self):
        self.exit()             # exit() is available in wuy.Window !

if __name__=="__main__":
    index()
    
