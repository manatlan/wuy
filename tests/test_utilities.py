# -*- coding: utf-8 -*-
import wuy, sys, asyncio, os
from datetime import date, datetime


def test_isFreePort():
    ll = [wuy.isFree("localhost", p) for p in [22, 23, 445]]
    assert False in ll


def test_path():
    assert not hasattr(sys, "_MEIPASS")
    assert wuy.path("jo") == os.path.join(os.getcwd(), "jo")


def test_pathFrozen():
    sys._MEIPASS = "kiki"
    assert wuy.path("jo").replace("\\", "/") == "kiki/jo"
    delattr(sys, "_MEIPASS")
    assert not hasattr(sys, "_MEIPASS")


def test_getname():
    assert wuy.getname("jo") == "jo"
    assert wuy.getname("jo.html") == "jo"
    assert wuy.getname("jim/jo") == "jim.jo"
    assert wuy.getname("jim/jo.html") == "jim.jo"
