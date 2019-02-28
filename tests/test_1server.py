# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os


def test_a_server():
    class saeff(wuy.Server):
        "I'm a server"

        def init(self):
            asyncio.get_event_loop().call_later(2, self.exit)

    saeff()
    assert "saeff" in wuy.currents
