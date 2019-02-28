# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os


def test():
    class aeff(wuy.Window):
        "test double open"
        size = (100, 100)

        def init(self):
            asyncio.get_event_loop().call_later(2, self.exit)

    aeff()
    aeff()
