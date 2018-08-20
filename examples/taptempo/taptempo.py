#!/usr/bin/python3
# -*- coding: utf-8 -*-
import wuy,datetime

# use docstring as content for the html response

class taptempo(wuy.Window):
    """ <button onclick="wuy.tic().then(x=>{document.querySelector('#tempo').innerHTML=x})">Tap Tempo</button> 
        <span id="tempo"></span>
    """
    size=(100,60)
    t=[]

    def tic(self):
        self.t.append( datetime.datetime.now() )
        ll=[ (j-i).microseconds for i, j in zip(self.t[:-1], self.t[1:]) ][-5:]
        if ll: 
            return int(60000000*len(ll)/sum(ll))

if __name__=="__main__":
    taptempo()