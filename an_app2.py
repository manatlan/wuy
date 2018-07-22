# -*- coding: utf-8 -*-
import wuy

# it's the future ... (just ask name and return it)

class askName(wuy.Window):    # name the class as the web/<class_name>.html
    size=(200,200)
    
    name=None

    def post(self,name):
        self.name=name.strip()
        if self.name:
            self.exit()


if __name__=="__main__":
    x=askName()
    print("Your name is '%s' !!!" % x.name)
