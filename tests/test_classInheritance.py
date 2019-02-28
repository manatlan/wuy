# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os
from datetime import date, datetime
import unittest


def test():
    class More:
        def jo2():
            pass

    class saeff(wuy.Server, More):
        size = (100, 100)

        def init(self):
            asyncio.get_event_loop().call_later(2, self.exit)

        def jo1():
            pass

    x = saeff()
    assert "jo1" in x._routes.keys()
    assert "jo2" in x._routes.keys()
