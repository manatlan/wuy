# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os


def test():
    class saeff1(wuy.Server):
        "I'm a server"

        def init(self):
            asyncio.get_event_loop().call_later(2, self.exit)

    class saeff2(wuy.Server):
        "I'm a server, and I will killed by saeff1"
        pass

    wuy.Server.run()
    assert "saeff1" in wuy.currents
    assert "saeff2" in wuy.currents
