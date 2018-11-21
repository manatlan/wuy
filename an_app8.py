# -*- coding: utf-8 -*-
import wuy


class AddMore1:
    def beep1(self):
        print("\aBEEEP1")

class AddMore2:
    def beep2(self):
        print("\aBEEEP2")

class alone(wuy.Window,AddMore1,AddMore2):
    """ <button onclick="wuy.beep()">BEEP</button>
        <button onclick="wuy.beep1()">BEEP1</button>
        <button onclick="wuy.beep2()">BEEP2</button> """
    size=(100,100)

    def beep(self):
        print("\aBEEEP")

if __name__=="__main__":
    alone()