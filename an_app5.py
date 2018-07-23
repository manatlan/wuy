# -*- coding: utf-8 -*-
import wuy, asyncio,datetime

# it's the future ... (example of running long request)

class updater(wuy.Window):    # name the class as the web/<class_name>.html
    size=(300,100)

    def init(self):
        self.emit("event",str(datetime.datetime.now()))
        asyncio.get_event_loop().call_later(2, self.init)        

if __name__=="__main__":
    updater()
