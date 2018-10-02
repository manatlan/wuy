#!/usr/bin/python3 -u
import wuy,os,vbuild

class index(wuy.Window):

    size=(400,200)

    def _render(self,path): #here is the magic
        # this method is overrided, so you can render what you want

        # load your template (from web folder)
        with open( os.path.join(path,"web","index.html") ) as fid:
            content=fid.read()
        
        # load all vue/sfc components
        v=vbuild.render( path+"web/*.vue" )

        # and inject them in your template
        return content.replace("<!-- HERE -->",str(v))

if __name__=="__main__":
    index()
