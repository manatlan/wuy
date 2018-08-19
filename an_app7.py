# -*- coding: utf-8 -*-
import wuy

# use docstring as content for the html response

class alone(wuy.Window):
    """ <button onclick="wuy.beep()">BEEP</button> """
    size=(100,100)

    def beep(self):
        print("\aBEEEP")

if __name__=="__main__":
    alone()