# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os
from datetime import date, datetime


def test():
    class aeff(wuy.Window):
        size = (100, 100)

        def init(self):
            asyncio.get_event_loop().call_later(2, self.exit)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # the following line is needed
    # because pytest seems to execute from a different path
    # then the executable one (think freezed)
    # ex: it works without it, in a real context
    # ex: it's needed when pytest execute the test
    # IRL : it's not needed to change the path
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    wuy.PATH = os.getcwd()  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    cf = "web/aeff.html"
    if os.path.isfile(cf):
        os.unlink(cf)
    aeff()
    assert os.path.isfile(cf), "a default file can't be created !!!"
    os.unlink(cf)
