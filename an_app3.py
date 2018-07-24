# -*- coding: utf-8 -*-
import wuy

# it's the future ... (example of passing kwargs to js, and window can open another window !!!!)

class alert(wuy.Window):    # name the class as the web/<class_name>.html
    size=(200,100)

    def next(self):
        alert(msg='"Madame"',cpt=self.cpt+1)    # open another window in the rpc call !!

if __name__=="__main__":
    alert(msg="El'Senôr",cpt=1)
