import wuy,os

class selectAFile(wuy.Window):
    """ 
    <style>
        body {font-family:sans-serif;font-size:0.8em;cursor:default !important;white-space: nowrap;}
        .folder {cursor:pointer;color:blue}
        div{border-bottom:1px dotted #DDD;padding:2px}
        div:hover{background:#EEE}
    </style>
    <span id="output"></span>
    <script>
        document.addEventListener('contextmenu', e => e.preventDefault())
        var o=document.querySelector("#output");

        async function list(path = wuy.folder) {
            o.innerHTML=""
            document.title=path;
            for(item of await wuy.list(path)) {
                let d=document.createElement("div")
                d.innerHTML=item.name;
                d.path=item.path;
                if(item.isdir) {
                    d.innerHTML="&#128193; "+item.name;
                    d.setAttribute("class","folder")
                    d.onclick= function() { list( this.path )}
                }
                else
                    d.onclick= function() { wuy.select( this.path )}
                o.appendChild(d)
            }
        }

        document.addEventListener("init", x=>list() );
    </script>
    """

    size=(400,600)
    path=None

    def list(self,path):
        np=lambda x: os.path.realpath(os.path.join(path,x))
        ll=[ dict(name="..",isdir=True, path=np("..")) ]
        try:
            ll.extend( [dict(name=i,isdir=os.path.isdir( np(i) ),path=np(i)) for i in os.listdir(path)] )
        except PermissionError:
            pass
        return ll

    def select(self,path):
        self.path=path
        self.exit()

x=selectAFile(log=False, folder=os.getcwd())
print(x.path)
