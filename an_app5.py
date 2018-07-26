# -*- coding: utf-8 -*-
import wuy

# it's the future ... (call a http service during an async rpc method call)

class fetch(wuy.Window):    # name the class as the web/<class_name>.html
    size=(400,400)

    async def requestWeb(self,url):
        return (await wuy.request(url)).content # use wuy.request(url,data=None,headers={})

if __name__=="__main__":
    fetch()




