# -*- coding: utf-8 -*-
import wuy

# it's the future ... (example of passing kwargs to js)

class alert(wuy.Window):    # name the class as the web/<class_name>.html
    size=(200,70)
    
    def quit(self):
        self.exit()

if __name__=="__main__":
    alert(port=8001,msg="Tintin")
    alert(port=8002,msg="Milou")
