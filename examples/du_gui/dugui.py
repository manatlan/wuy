#!/usr/bin/python3 -u
import wuy,os
import subprocess

def getSize(path):
    print(path)
    try:
        return int(str(subprocess.check_output(["du","-sb",path]),"utf8").split("\t")[0])
    except:
        return 0

class duGui(wuy.Window):
    """ 
    <style>
        body {font-family:sans-serif;font-size:0.8em;cursor:default !important;white-space: nowrap;}
        .folder {cursor:pointer;color:blue}
        div{border-bottom:1px dotted #DDD;padding:2px}
        div:hover{background:#EEE}
        div > span {float:right}
    </style>
    <span id="output"></span>
    <script>
        document.addEventListener('contextmenu', e => e.preventDefault())
        var o=document.querySelector("#output");

        function bytesToSize(bytes) {
            var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            if (bytes == 0) return '0 Byte';
            var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
        }

        async function list(path = wuy.folder) {
            o.innerHTML="Getting a list of files sizes in <b>"+path+"</b><br><br><b>Just wait ...</b>"
            document.title=path;
            var ll=await wuy.list(path)
            o.innerHTML=""
            for(item of ll) {
                let d=document.createElement("div")
                d.innerHTML=item.name;
                d.path=item.path;
                if(item.isdir) {
                    d.innerHTML="&#128193; "+item.name;
                    d.setAttribute("class","folder")
                    d.onclick= function() { list( this.path )}
                }
                d.innerHTML+="<span>"+(item.size>0?bytesToSize(item.size):'')+"</span>";
                o.appendChild(d)
            }
        }

        wuy.init( function() {list()} );
    </script>
    """

    size=(400,600)
    path=None

    def list(self,path):
        np=lambda x: os.path.realpath(os.path.join(path,x))
        try:
            ll=[dict(name=i,isdir=os.path.isdir( np(i) ),path=np(i),size=getSize(np(i))) for i in os.listdir(path)]
        except:
            ll=[]
        ll.sort(key=lambda i: -i["size"])
        return [ dict(name="..",isdir=True, path=np(".."), size=0) ] + ll


if __name__=="__main__":
    try:
        if subprocess.check_call(["which","du"])==0:
            duGui(log=False, folder=os.path.expanduser("~"))
        else:
            raise
    except:
        print("Only available on platform which have 'du' ;-) (linux tool)")
