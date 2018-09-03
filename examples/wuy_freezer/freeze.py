#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import sys,wuy,os,tempfile

try:
    from PyInstaller import __main__ as pyi
except ImportError:
    print("Please, install pyinstaller (pip3 install pyinstaller)")
    sys.exit(-1)

class gui(wuy.Window):
    """ 
    <title>Wuy Freezer</title>
    <style>
        body {font-family:sans-serif;font-size:0.8em;cursor:default !important;white-space: nowrap;background:#EEE}
        .folder {color:blue}
        div#output {display:block;height:200px;overflow-y:scroll;border:1px solid #888;background:white}
        div#output div{border-bottom:1px dotted #DDD;padding:2px;cursor:pointer;}
        div#output div:hover{background:#EEE}
    </style>
    <b>Select a py3 file (main wuy script)</b> :
    <div id="output"></div>
    <form onsubmit="this.btn.hidden=true;wuy.select( this.path.value, this.inConsole.checked, this.addWeb.checked ); return false">
        Wuy Script<br/><input name="path" style="width:100%" disabled/><br/>
        <label><input type="checkbox" name="addWeb"> Include its web folder</label><br/>
        <label><input type="checkbox" name="inConsole"> With a output console</label><br/>
        <br/>
        <input type="submit" name="btn" disabled=true value="Build Exe (and look into the console)"/>
    </form>
    <script>
        document.addEventListener('contextmenu', e => e.preventDefault())
        var o=document.querySelector("#output");

        async function list(path = wuy.folder) {
            o.innerHTML=""
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
                    d.onclick= function() { document.forms[0].btn.disabled=false;document.forms[0].path.value=this.path }
                o.appendChild(d)
            }
        }

        document.addEventListener("init", x=>list() );
    </script>
    """

    size=(400,400)

    def list(self,path):
        np=lambda x: os.path.realpath(os.path.join(path,x))
        ll=[ dict(name="..",isdir=True, path=np("..")) ]
        try:
            ll.extend( [dict(name=i,isdir=os.path.isdir( np(i) ),path=np(i)) for i in os.listdir(path)] )
            ll=list(filter(lambda x: x["isdir"] or x["name"].lower().endswith(".py"),ll))
        except PermissionError:
            pass
        return ll

    def select(self,path,inConsole,addWeb):
        build(path,inConsole,addWeb)
        self.exit()

def build(path,inConsole=False,addWeb=False):
    params=[path,"--noupx","--onefile"]

    if not inConsole:
        params.append( "--noconsole")
    
    web=os.path.join( os.path.dirname(path), "web" )
    if addWeb and os.path.isdir(web):
        sep = (os.name == 'nt') and ";" or ":"
        params.append("--add-data=%s%sweb" % (web,sep))

    temp=os.path.join(tempfile.gettempdir(),".build")
    params.append( "--workpath" )
    params.append( temp )

    params.append( "--distpath" )
    params.append( os.path.dirname(path) )

    print( "PYINSTALLER:",params )
    pyi.run( params )

if __name__=="__main__":
    gui(log=True, folder=os.getcwd(),port=9999)
