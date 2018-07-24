# -*- coding: utf-8 -*-
import wuy

# it's the future ... (the server never ends or open a browser)
# a simple tchat for many clients
# (with IE11 compatibility, see tchat.html which include a polyfill)

class tchat(wuy.Server):    # name the class as the web/<class_name>.html
    
    def post(self,txt):
        self.emit( "addTxt", txt)   # emit an event to all clients (me too !)

if __name__=="__main__":
    print("Open your browser (manually) to http://localhost:8080/tchat.html (as many as you want)")
    tchat() # can't exit !
