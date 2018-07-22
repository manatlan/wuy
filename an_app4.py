# -*- coding: utf-8 -*-
import wuy

# it's the future ... (example of running long request)
import asyncio

  

class doSomething(wuy.Window):    # name the class as the web/<class_name>.html
    size=(200,70)
    
    def doSyncQuick(self):
        return "s quick"

    def doSyncLong(self):
        import time
        time.sleep(2)
        return "s long"

    def doASyncLong(self):

        async def takeLong():
            await asyncio.sleep(3)
            self.emit("event","task ok")

        asyncio.ensure_future(takeLong())
        return "task started"

if __name__=="__main__":
    doSomething()
