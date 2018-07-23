# -*- coding: utf-8 -*-
import wuy, asyncio

# it's the future ... (example of running long request)

class doSomething(wuy.Window):    # name the class as the web/<class_name>.html
    size=(300,300)

    def doSyncQuick(self):
        return "quick"

    def doSyncLong(self):           # run synchro (hangs the ui)
        import time
        time.sleep(2)
        return "long"

    async def doASyncLong(self):    # run asynchro !!! (it doesn't hang the UI !)
        await asyncio.sleep(3)
        return "async long"

if __name__=="__main__":
    doSomething(port=8081)
