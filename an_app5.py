# -*- coding: utf-8 -*-
import wuy,re

# call a http service during an async rpc method call

class fetch(wuy.Window):    # name the class as the web/<class_name>.html
    size=wuy.FULLSCREEN

    async def feed(self):
        r=(await wuy.request("https://www.reddit.com/r/pics/.rss")).content
        return re.findall("https://i.redd.it/[^\.]+\....",r)

if __name__=="__main__":
    fetch() # CTRL-W or alt-f4 to quit !




