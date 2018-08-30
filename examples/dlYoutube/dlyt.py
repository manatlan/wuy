#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import wuy,urllib,aiohttp

try:
    import youtube_dl as yt
except ImportError:
    print("Please, install youtube-dl (pip3 install youtube-dl)")
    sys.exit(-1)

import unicodedata,string

def removeDisallowedFilenameChars(filename):
    VALID = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(chr(c) for c in cleanedFilename if chr(c) in VALID)


class dlYoutube(wuy.Window):
    """ <form onsubmit="if(this.q.value.trim()) aff( this.q.value ); return false">
        <input name="q" value="" style="width:100%" placeholder=".... enter a youtube id or url ..."/><br/>
        <input type="submit" value="ok"/>
    </form>
    <div id="r"></div>
    <script>
    async function aff(q) {
        var info=await wuy.get( q );
        var h=`<h4>${info.title}</h4>`;
        for(var i of info.formats)
                h+=`<li><a href='#' onclick="dl('${i.url}','${info.title}(${i.format}).${i.ext}')">${i.format} - ${i.filesize || ''}</a></li>`
        document.querySelector("#r").innerHTML=h;
    }

    async function dl(url,title) {
        document.querySelector("body").innerHTML="Downloading <i>"+title+"</i><br><br><b id='p'>0%</b>";

        wuy.on("percent", function( percent ) {
            document.querySelector("#p").innerHTML=percent+"%";
        })

        await wuy.dl(url,title);
        document.querySelector("body").innerHTML="Ok, downloaded !";
    }
    </script>
    """
    size=(500,200)

    def get(self,q):
        if "http" in q.lower():
            u=q.strip()
        else:
            u='https://www.youtube.com/watch?v='+q
        y = yt.YoutubeDL()
        return y.extract_info(u, download=False)

    async def dl(self,url,name):
        name=removeDisallowedFilenameChars(str(name))
        with open(name,"wb+") as fid:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as stream:
                    chunk_size=1024*32
                    size=int(stream.headers.get("Content-Length",1))
                    while True:
                        chunk = await stream.content.read(chunk_size)
                        if not chunk: break
                        fid.write(chunk)                    
                        self.emit("percent",int(( fid.tell()/size)*100))
        return name
            
if __name__=="__main__":
    dlYoutube(log=False)
