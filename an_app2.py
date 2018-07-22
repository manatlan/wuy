# -*- coding: utf-8 -*-
import wuy

# it's the future ... (same as simple.py, but with class app concept)

class askName(wuy.Window):    # name the class as the web/<class_name>.html
    size=(200,200)
    
    name=None

    def post(self,name):
        self.name=name
        self.exit()


if __name__=="__main__":
    x=askName()
    print("Your name is",x.name,"!!!")
