# -*- coding: utf-8 -*-
import wuy

class m1(wuy.Server):    # page m1 interact with this class
    def post(self,txt):
        self.emit( "addTxt", "1:"+txt)   # emit an event to all clients (me too !)

class m2(wuy.Server):    # page m2 interact with this class
    def post(self,txt):
        self.emit( "addTxt", "2:"+txt)   # emit an event to all clients (me too !)

if __name__=="__main__":
    wuy.Server.run()
