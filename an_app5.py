# -*- coding: utf-8 -*-
import wuy, aiohttp

# it's the future ... (call a http service during an async rpc method call)

class fetch(wuy.Window):    # name the class as the web/<class_name>.html
    size=(400,400)

    async def requestWeb(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()

if __name__=="__main__":
    fetch()
