# -*- coding: utf-8 -*-
import wuy
import asyncio

# Simulate long running process with progress bar client side

class progress(wuy.Window):    # name the class as the web/<class_name>.html

    # size=wuy.FULLSCREEN
    size=(500,200)

    async def doTheJob(self,pb,speed):
        for i in range(101):
            await asyncio.sleep(speed)    # simulate the job
            self.emit("percent",pb,i)
        return "Job Done %s!" % pb

if __name__=="__main__":
    progress()


