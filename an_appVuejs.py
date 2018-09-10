# -*- coding: utf-8 -*-
import wuy, asyncio,datetime

# it's the future ... (A vuejs app, and use the special method init to do something before start)

class vuejs(wuy.Window):    # name the class as the web/<class_name>.html
    size=(400,200)

    def init(self):             #<- special method which is called at the start !
        self.emit("setTheDate",datetime.datetime.now())
        asyncio.get_event_loop().call_later(1, self.init)

    def inc(self,value):
        return value+1

if __name__=="__main__":
    vuejs()
