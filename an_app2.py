# -*- coding: utf-8 -*-
import wuy

# it's the future ... (just ask name and return it)

class askName(wuy.Window):    # name the class as the web/<class_name>.html
    size=(300,70)

    name=None   # <- a placeholder

    def post(self,name):
        if name.strip():
            self.name=name.strip()
            self.exit()

if __name__=="__main__":
    x=askName(port=8888)
    if x.name:
        print("Your name is '%s' !!!" % x.name)
    else:
        print("You are unamed ?! ;-) ")
