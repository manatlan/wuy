#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2019 manatlan manatlan[at]gmail(dot)com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# https://github.com/manatlan/reqman
# #############################################################################

__version__ = "1.4.4.0"

import asyncio
import collections
import copy
import datetime
import email
import glob
import html
import http.client
import http.cookiejar
import io
import itertools
import json
import os
import re
import socket
import sys
import traceback
import typing as T
import urllib.parse
import urllib.request
import xml.dom.minidom
from enum import Enum

import httpcore
import yaml  # see "pip install pyyaml"

###############################################################################################################
###############################################################################################################
###############################################################################################################


class NotFound:
    pass


class RMException(Exception):
    pass


class RMNonPlayable(Exception):
    pass


REQMAN_CONF = "reqman.conf"
KNOWNVERBS = set(
    ["GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS", "TRACE", "PATCH", "CONNECT"]
)

###########################################################################
## Utilities
###########################################################################
try:  # colorama is optionnal
    from colorama import init, Fore, Style

    init()

    def colorize(color: int, t: str) -> T.Union[str, None]:
        return color + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL if t else None

    cy = lambda t: colorize(Fore.YELLOW, t)
    cr = lambda t: colorize(Fore.RED, t)
    cg = lambda t: colorize(Fore.GREEN, t)
    cb = lambda t: colorize(Fore.CYAN, t)
    cw = lambda t: colorize(Fore.WHITE, t)
except ImportError:
    cy = cr = cg = cb = cw = lambda t: t


def chardet(s: str) -> str:
    """guess encoding of the string 's' -> cp1252 or utf8"""
    u8 = "çàâäéèêëîïôûù"
    cp = u8.encode("utf8").decode("cp1252")

    cu8, ccp = 0, 0
    for c in u8:
        cu8 += s.count(c)
    for c in cp:
        ccp += s.count(c)

    if cu8 >= ccp:
        return "utf8"
    else:
        return "cp1252"


def yamlLoad(fd) -> dict:  # fd is an io thing
    b = fd.read()
    if type(b) == bytes:
        try:
            b = str(b, "utf8")
        except UnicodeDecodeError:
            b = str(b, "cp1252")
    else:
        encoding = chardet(b)
        b = b.encode(encoding).decode("utf8")
    return yaml.load(b, Loader=yaml.FullLoader)


def dict_merge(dst: dict, src: dict) -> None:
    """ merge dict 'src' in --> dst """
    for k, v in src.items():
        if (
            k in dst
            and isinstance(dst[k], dict)
            and isinstance(src[k], collections.abc.Mapping)
        ):
            dict_merge(dst[k], src[k])
        else:
            if k in dst and isinstance(dst[k], list) and isinstance(src[k], list):
                dst[k] += src[k]
            else:
                dst[k] = src[k]


def mkUrl(protocol: str, host: str, port=None) -> str:
    port = ":%s" % port if port else ""
    return "{protocol}://{host}{port}".format(**locals())


def prettify(txt: str, indentation: int = 4) -> str:
    try:
        x = xml.dom.minidom.parseString(txt).toprettyxml(indent=" " * indentation)
        x = "\n".join(
            [s for s in x.splitlines() if s.strip()]
        )  # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/
        return x
    except:
        try:
            return json.dumps(json.loads(txt), indent=indentation, sort_keys=True)
        except:
            return txt


def jpath(elem, path: str) -> T.Union[int, T.Type[NotFound], str]:
    for i in path.strip(".").split("."):
        try:
            if type(elem) == list:
                if i == "size":
                    return len(elem)
                else:
                    elem = elem[int(i)]
            elif type(elem) == dict:
                if i == "size":
                    return len(list(elem.keys()))
                else:
                    elem = elem.get(i, NotFound)
            elif type(elem) == str:
                if i == "size":
                    return len(elem)
        except (ValueError, IndexError) as e:
            return NotFound
    return elem


###########################################################################
## http request/response
###########################################################################

class Request:
    def __init__(
        self,
        protocol: str,
        host: str,
        port,
        method: str,
        path: str,
        body=None,
        headers: dict = {},
    ) -> None:
        self.protocol = protocol
        self.host = host
        self.port = port
        self.method = method
        self.path = path
        self.body = body
        self.headers = {}

        if self.protocol:
            self.url = mkUrl(self.protocol, self.host, self.port) + self.path
        else:
            self.url = None

        self.headers.update(headers)

    def __repr__(self) -> str:
        return cy(self.method) + " " + self.path


class Content:
    def __init__(self, content) -> None:
        self.__b = content if type(content) == bytes else bytes(str(content), "utf8")

    def toBinary(self) -> bytes:
        return self.__b

    def __repr__(self) -> str:
        try:
            return str(self.__b, "utf8")  # try as utf8 ...
        except UnicodeDecodeError:
            try:
                return str(self.__b, "cp1252")  # try as cp1252 ...
            except UnicodeDecodeError:
                # fallback to a *** binary representation ***
                return "*** BINARY SIZE(%s) ***" % len(self.__b)

    def __contains__(self, key: str) -> bool:
        return key in str(self)


class BaseResponse:
    time = None
    status = None
    content = None
    headers = {}
    info = None
    url=""


class Response(BaseResponse):
    def __init__(self, status, body, headers, url, info=None) -> None:
        self.status = int(status)
        self.content = Content(body)
        self.headers = dict(headers)  # /!\ cast list of 2-tuple to dict ;-(
        # eg: if multiple "set-cookie" -> only the last is kept
        self.info = info
        self.url=url # just to extract cookie

    def __repr__(self) -> str:
        return str(self.status)


class ResponseError(BaseResponse):
    def __init__(self, m) -> None:
        self.status = None
        self.content = m
        self.headers = {}
        self.info = ""
        self.url=None

    def __repr__(self) -> str:
        return "ERROR: %s" % (self.content)

class CookieStore(http.cookiejar.CookieJar):
    """ Manage cookiejar for httplib-like """

    def __init__(self, ll: T.List[dict]=[]) -> None:
        http.cookiejar.CookieJar.__init__(self)
        for c in ll:
            self.set_cookie( http.cookiejar.Cookie(**c) )    

    def update(self, req: Request) -> dict:
        """return appended headers"""
        if req.url:
            r = urllib.request.Request(req.url)
            self.add_cookie_header(r)
            req.headers.update( dict(r.header_items()) )
            return dict(r.header_items())

    def extract(self, res: BaseResponse) -> None:
        if res.url:
            headers=res.headers.items()

            class FakeResponse(http.client.HTTPResponse):
                def __init__(self, headers=[], url=None) -> None:
                    """
                    headers: list of RFC822-style 'Key: value' strings
                    """
                    m = email.message_from_string("\n".join(headers))
                    self._headers = m
                    self._url = url

                def info(self):
                    return self._headers

            response = FakeResponse([": ".join([k, v]) for k, v in headers], res.url)
            self.extract_cookies(response, urllib.request.Request(res.url))

    def export(self) -> T.List[dict]:
        ll=[]
        for i in self:
            ll.append( {n if n!="_rest" else "rest":getattr(i,n) for n in "version,name,value,port,port_specified,domain,domain_specified,domain_initial_dot,path,path_specified,secure,expires,discard,comment,comment_url,_rest".split(",")} )
        return ll


AHTTP = httpcore.AsyncClient(verify=False)


async def dohttp(r: Request, timeout=None) -> BaseResponse:
    try:
        body=r.body
        if body is None:
            body=""
        elif type(body)!=str:
            body=json.dumps(body)
        rr = await AHTTP.request(
            r.method,
            r.url,
            data=body.encode(),
            headers=r.headers,
            allow_redirects=False,
            timeout=httpcore.TimeoutConfig(timeout),
        )
        info = "%s %s %s" % (rr.protocol, int(rr.status_code), rr.reason_phrase)

        return Response(rr.status_code, rr.content, dict(rr.headers), r.url, info)
    except httpcore.exceptions.ReadTimeout:
        return ResponseError("Response timeout")
    except httpcore.exceptions.ConnectTimeout:
        return ResponseError("Response timeout")
    except httpcore.exceptions.Timeout:
        return ResponseError("Response timeout")
    except httpcore.exceptions.WriteTimeout:
        return ResponseError("Response timeout")
    except KeyError:  # KeyError: <httpcore.dispatch.connection.HTTPConnection object at 0x7fadbf88e0f0>
        return ResponseError("Response timeout")
    # except socket.gaierror:
    except OSError:
        return ResponseError("Server is down ?!")


###############################################################################################################
###############################################################################################################
###############################################################################################################


###########################################################################
## Reqs manage
###########################################################################
class Test(int):
    """ a boolean with a name """

    def __new__(cls, value: int, nameOK: str, nameKO: str):
        s = super(Test, cls).__new__(cls, value)
        if value:
            s.name = nameOK
        else:
            s.name = nameKO
        return s



def getValOpe(v):
    try:
        if type(v) == str and v.startswith("."):
            g = re.match(r"^\. *([!=<>]{1,2}) *(.+)$", v)
            if g:
                op, v = g.groups()
                vv = yaml.load(v, Loader=yaml.FullLoader)
                if op == "==":  # not needed really, but just for compatibility
                    return vv, lambda a, b: b == a, "=", "!="
                elif op == "=":  # not needed really, but just for compatibility
                    return vv, lambda a, b: b == a, "=", "!="
                elif op == "!=":
                    return vv, lambda a, b: b != a, "!=", "="
                elif op == ">=":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b >= a or False,
                        ">=",
                        "<",
                    )
                elif op == "<=":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b <= a or False,
                        "<=",
                        ">",
                    )
                elif op == ">":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b > a or False,
                        ">",
                        "<=",
                    )
                elif op == "<":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b < a or False,
                        "<",
                        ">=",
                    )
    except (
        yaml.scanner.ScannerError,
        yaml.constructor.ConstructorError,
        yaml.parser.ParserError,
    ):
        pass
    return v, lambda a, b: a == b, "=", "!="


def strjs(x) -> str:
    return json.dumps(x, ensure_ascii=False)


class TestResult(list):
    def __init__(self, req, res, tests, doc=None) -> None:
        self.req = req
        self.res = res
        self.doc = doc

        insensitiveHeaders = (
            {k.lower(): v for k, v in self.res.headers.items()} if self.res else {}
        )

        results = []
        for test in tests:
            what, value = list(test.keys())[0], list(test.values())[0]

            testContains = False

            # get the value to compare with value --> tvalue
            if what == "content":
                testContains = True
                tvalue = str(self.res.content)
            elif what == "status":
                testContains = False
                tvalue = self.res.status
            elif what.startswith("json."):
                testContains = False
                try:
                    jzon = json.loads(str(self.res.content))
                    tvalue = jpath(jzon, what[5:])
                    tvalue = None if tvalue is NotFound else tvalue
                except Exception as e:
                    tvalue = None
            else:  # headers
                testContains = True
                tvalue = insensitiveHeaders.get(what.lower(), "")

            # test if all match as json (list, dict, str ...)
            try:
                j = lambda x: json.dumps(
                    json.loads(x) if type(x) in [str, bytes] else x, sort_keys=True
                )
                matchAll = j(value) == j(tvalue)
            except json.decoder.JSONDecodeError as e:
                matchAll = False

            if matchAll:
                test, opOK, opKO, val = True, "=", "!=", value
            else:
                # ensure that we've got a list
                values = [value] if type(value) != list else value
                opOK, opKO = None, None
                bool = False
                for value in values:  # match any
                    if testContains:
                        value, ope, opOK, opKO = (
                            value,
                            lambda x, c: x in c,
                            "contains",
                            "doesn't contain",
                        )
                    else:
                        value, ope, opOK, opKO = getValOpe(value)

                    bool = ope(value, tvalue)
                    if bool:
                        break

                if len(values) == 1:
                    test, opOK, opKO, val = bool, opOK, opKO, value
                else:
                    test, opOK, opKO, val = (
                        bool,
                        "matchs any",
                        "doesn't match any",
                        values,
                    )

            results.append(
                Test(
                    test,
                    what + " " + opOK + " " + strjs(val),  # test name OK
                    what + " " + opKO + " " + strjs(val),  # test name KO
                )
            )

        list.__init__(self, results)

    def __repr__(self) -> str:
        ll = [""]
        ll.append(
            cy("*")
            + " %s --> %s"
            % (self.req, cw(str(self.res)) if self.res else cr("Not callable"))
        )
        for t in self:
            ll.append("  - %s: %s" % (cg("OK") if t == 1 else cr("KO"), t.name))
        return "\n".join(ll)


def getVar(env: dict, var: str) -> T.Any:
    if var in env:
        return txtReplace(env, env[var])
    elif "|" in var:
        key, method = var.split("|", 1)

        content = env.get(key, key)  # resolv keys else use it a value !!!!!
        content = txtReplace(env, content)
        for m in method.split("|"):
            content = transform(content, env, m)
            content = txtReplace(env, content)
        return content

    elif "." in var:
        val = jpath(env, var)
        if val is NotFound:
            raise RMNonPlayable(
                "Can't resolve '%s'" % var
            )
        return txtReplace(env, val)
    else:
        raise RMNonPlayable(
            "Can't resolve '%s'" % var
        )


def DYNAMIC(x, env: dict) -> T.Union[str, None]:
    pass  # will be overriden (see below vv)


def transform(
    content: T.Union[str, None], env: dict, methodName: str
) -> T.Union[str, None]:
    if methodName:
        if methodName in env:
            code = getVar(env, methodName)
            try:
                exec(
                    "def DYNAMIC(x,ENV):\n"
                    + ("\n".join(["  " + i for i in code.splitlines()])),
                    globals(),
                )
            except Exception as e:
                raise RMException(
                    "Error in declaration of method " + methodName + " : " + str(e)
                )
            try:
                if content is not None:
                    x = json.loads(content)
                else:
                    x = None
            except (json.decoder.JSONDecodeError, TypeError):
                x = content
            try:
                if transform.path:
                    curdir = os.getcwd()
                    os.chdir(transform.path)
                else:
                    curdir = None
                content = DYNAMIC(x, env)
            except Exception as e:
                raise RMException(
                    "Error in execution of method " + methodName + " : " + str(e)
                )
            finally:
                if curdir:
                    os.chdir(curdir)
        else:
            raise RMException(
                "Can't find method "
                + methodName
                + " in : "
                + ", ".join(list(env.keys()))
            )

    return content


transform.path = None  # change cd cwd for transform methods when executed


def objReplace(env: dict, txt: str) -> T.Any:  # same as txtReplace() but for "object" (json'able)
    obj = txtReplace(env, txt)
    try:
        obj = json.loads(obj)
    except (json.decoder.JSONDecodeError, TypeError):
        pass
    return obj


def txtReplace(env: dict, txt) -> T.Any:
    if env and txt and isinstance(txt, str):
        for vvar in re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt):
            var = vvar[2:-2]

            try:
                val = getVar(
                    env, var
                )  # recursive here ! (if myvar="{{otherVar}}"", redo a pass to resolve otherVar)
            except RuntimeError:
                raise RMException("Recursion trouble for '%s'" % var)

            if val is NotFound:
                raise RMNonPlayable(
                    "Can't resolve '%s'" % var
                )
            else:
                if type(val) != str:
                    if val is None:
                        val = "null"
                    elif val is True:
                        val = "true"
                    elif val is False:
                        val = "false"
                    elif type(val) in [list, dict]:
                        val = json.dumps(val)
                    elif type(val) == bytes:
                        val = val  # keep BYTES !!!!!!!!!!!!!!
                    else:  # int, float, ...
                        val = json.dumps(val)

                if type(val) != bytes:
                    txt = txt.replace(vvar, val)
                else:
                    return val  # if bytes, return directly the bytes !!!

    return txt


def alwaysReplaceTxt(d, v):
    try:
        return txtReplace(d, v)
    except RMNonPlayable as e:
        return v


def warn(*m):
    print("***WARNING***", *m)


def getTests(y: dict) -> list:
    """ Get defined tests as list ok dict key:value """
    if y:
        tests = y.get("tests", [])
        if type(tests) == dict:
            warn(
                "'tests:' should be a list of mono key/value pairs (ex: '- status: 200')"
            )
            tests = [{k: v} for k, v in dict(tests).items()]
        return tests
    else:
        return []


def getHeaders(y: dict) -> dict:
    """ Get defined headers as dict """
    if y:
        headers = y.get("headers", {})
        if type(headers) == list:
            warn(
                "'headers:' should be filled of key/value pairs (ex: 'Content-Type: text/plain')"
            )
            headers = {list(d.keys())[0]: list(d.values())[0] for d in headers}
        headers={k:str(v) for k,v in headers.items()}
        return headers
    else:
        return {}



class Req(object):
    def __init__(
        self,
        method,
        path,
        body=None,
        headers={},
        tests=[],
        saves=[],
        params={},
        doc=None,
    ):  # body = str ou dict ou None
        self.method = method.upper()
        self.path = path
        self.body = body
        self.headers = headers
        self.tests = tests
        self.saves = saves
        self.params = params
        self.doc = doc

    def clone(self):
        return Req(
            self.method,
            self.path,
            copy.deepcopy(self.body),
            dict(self.headers),
            list(self.tests),
            list(self.saves),
            dict(self.params),
            self.doc,
        )

    def stest(self, env: dict = None) -> TestResult: #for pytests only ;-)
        return asyncio.run(self.test(env))

    async def test(self, env: dict = None) -> TestResult:

        if env is None: env={}
        cenv = env.copy()  # current env
        cenv.update(self.params)  # override with self params
        cenv = dict(cenv)
        errPath = (
            None
        )  # to handle NonPlayable test (not a error anymore, a TestResult is returned)

        # path ...
        try:
            path = txtReplace(cenv, self.path)
        except RMNonPlayable as e:
            path = self.path
            errPath = e  # to return a ResponseError on path replace trouble

        if cenv and (not path.strip().lower().startswith("http")) and ("root" in cenv):
            h = urllib.parse.urlparse(cenv["root"])
            if h.path and h.path[-1] == "/":
                if path[0] == "/":
                    path = h.path + path[1:]
                else:
                    path = h.path + path
            else:
                path = h.path + path
        else:
            h = urllib.parse.urlparse(path)
            path = h.path + ("?" + h.query if h.query else "")

        # headers ...
        headers = getHeaders(cenv).copy() if cenv else {}
        headers.update(self.headers)  # override with self headers
        headers = {
            k: alwaysReplaceTxt(cenv, v)
            for k, v in list(headers.items())
            if v is not None
        }

        # fill tests ...
        tests = getTests(cenv)
        tests += self.tests  # extends with self tests

        ntests = []
        for test in tests:
            key, val = list(test.keys())[0], list(test.values())[0]
            if type(val) == list:
                val = [alwaysReplaceTxt(cenv, i) for i in val]
            else:
                val = alwaysReplaceTxt(cenv, val)
            ntests.append({key: val})
        tests = ntests

        # body ...
        if self.body and not isinstance(self.body, str):

            # ================================
            def apply(body, method):
                if type(body) == list:
                    return [apply(i, method) for i in body]
                elif type(body) == dict:
                    return {k: apply(v, method) for k, v in body.items()}
                else:
                    return method(body)

            # ================================

            try:
                jrep = lambda x: objReplace(cenv, x)  # "json rep"
                body = apply(self.body, jrep)
                body = json.dumps(body)  # and convert to string !
            except RMNonPlayable as e:
                # return a TestResult Error ....
                body = self.body
        else:
            body = self.body
            while 1:
                precBody = body
                body = alwaysReplaceTxt(cenv, body)
                if body == precBody:
                    break


        if errPath:
            req = Request(
                h.scheme, h.hostname, h.port, self.method, path, body, headers
            )
            res = ResponseError(str(errPath))
            return TestResult(req, res, tests, self.doc)
        else:
            req = Request(
                h.scheme, h.hostname, h.port, self.method, path, body, headers
            )
            if h.hostname:

                timeout = cenv.get("timeout", None)
                try:
                    timeout = timeout and float(timeout) / 1000.0 or None
                except ValueError:
                    pass

                t1 = datetime.datetime.now()

                # set cookies in request according env
                cj=CookieStore( cenv.get("_cookies",[]) )
                cj.update(req)

                # make the request !!!!!!!!!!!!!!!!!!!!!!
                res = await dohttp(req, timeout)

                # extract cookies from response to the env
                cj.extract(res)
                env["_cookies"] = cj.export() # store in the env !


                res.time = datetime.datetime.now() - t1
                if isinstance(res, Response) and self.saves:
                    for save in self.saves:
                        dest = txtReplace(cenv, save)
                        if dest.lower().startswith("file://"):
                            name = dest[7:]
                            try:
                                with open(name, "wb+") as fid:
                                    fid.write(res.content.toBinary())
                            except Exception as e:
                                raise RMException(
                                    "Save to file '%s' error : %s" % (name, e)
                                )
                        else:
                            if dest:
                                try: # store in the env !
                                    env[dest] = json.loads(str(res.content))
                                except json.decoder.JSONDecodeError:
                                    env[dest] = str(res.content)

                return TestResult(req, res, tests, self.doc)
            else:
                # no hostname : no response, no tests ! (missing reqman.conf the root var ?)
                return TestResult(req, None, [], self.doc)

    def __repr__(self):
        return "<%s %s>" % (self.method, self.path)


def controle(keys: list, knowkeys: list) -> None:
    for key in keys:
        if key not in knowkeys:
            raise RMException("Not a valid entry '%s'" % key)


class Reqs(list):
    sequence="" # can be executed in parallel
    def __init__(self, fd: T.IO, env: dict = None) -> None:
        self.env = env or {}  # just for proc finding
        self.name = fd.name.replace("\\", "/") if hasattr(fd, "name") else "String"
        self.trs = []
        if not hasattr(fd, "name"):
            setattr(fd, "name", "<string>")
        try:
            l = yamlLoad(fd)
        except Exception as e:
            raise RMException("YML syntax in %s\n%s" % (fd.name or "<string>", e))

        procs = {}

        def feed(l):
            l = l if type(l) == list else [l]

            ll = []
            for entry in l:
                if not entry:
                    continue
                env = {}
                dict_merge(env, self.env)

                try:
                    if type(entry) != dict:
                        if type(entry) == str and entry == "break":
                            break
                        else:
                            raise RMException("no actions for %s" % entry)
                    action = list(
                        (KNOWNVERBS | set(["call"])).intersection(list(entry.keys()))
                    )
                    if len(action) > 1:
                        raise IndexError
                    else:
                        action = action[0]
                except IndexError:
                    action = None

                if action is not None:
                    # a real action (call a proc or a requests)
                    headers = getHeaders(entry)
                    tests = getTests(entry)
                    params = entry.get("params", {})
                    foreach = entry.get("foreach", [None])  # at least one iteration !
                    saves = entry.get("save", [])
                    saves = saves if type(saves) == list else [saves]

                    if type(params) == dict:
                        dict_merge(env, params)  # add current params (to find proc)
                    else:
                        raise RMException("params is not a dict : '%s'" % params)

                    if foreach and type(foreach) == str:
                        foreach = objReplace(env, foreach)

                    if action == "call":
                        controle(
                            entry.keys(),
                            ["headers", "tests", "params", "foreach", "save", "call"],
                        )

                        procnames = entry["call"]

                        if procnames and type(procnames) == str:
                            procnames = objReplace(env, procnames)

                        procnames = (
                            procnames if type(procnames) == list else [procnames]
                        )

                        for procname in procnames:
                            procname = objReplace(env, procname)
                            content = procs.get(procname, env.get(procname, None))
                            if content is None:
                                raise RMException(
                                    "unknown procedure '%s' is %s"
                                    % (procname, procs.keys())
                                )

                            for param in foreach:
                                if type(param) == str:
                                    param = objReplace(env, param)
                                for req in feed(content):
                                    newreq = req.clone()
                                    newreq.tests += tests  # merge tests
                                    dict_merge(newreq.headers, headers)  # merge headers
                                    dict_merge(newreq.params, params)  # merge params
                                    if param:
                                        dict_merge(
                                            newreq.params, param
                                        )  # merge foreach param
                                    newreq.saves += saves  # merge saves
                                    newreq.doc=alwaysReplaceTxt(newreq.params,newreq.doc) #new

                                    ll.append(newreq)
                    else:
                        controle(
                            entry.keys(),
                            [
                                "headers",
                                "doc",
                                "tests",
                                "params",
                                "foreach",
                                "save",
                                "body",
                            ]
                            + list(KNOWNVERBS),
                        )

                        body = entry.get("body", None)
                        doc = entry.get("doc", None)

                        if foreach and type(foreach) != list:
                            raise RMException("the foreach section is not a list ?!")

                        for param in foreach:
                            if type(param) == str:
                                param = objReplace(env, param)

                            lparams = {}
                            dict_merge(lparams, params)
                            if param:
                                dict_merge(lparams, param)

                            doc=alwaysReplaceTxt(lparams,doc) #new

                            ll.append(
                                Req(
                                    action,
                                    entry[action],
                                    body,
                                    headers,
                                    tests,
                                    saves,
                                    lparams,
                                    doc,
                                )
                            )

                elif len(entry) == 1 and type(list(entry.values())[0]) in [list, dict]:
                    # a proc declared
                    procname, content = list(entry.items())[0]
                    if procname in [
                        "headers",
                        "tests",
                        "params",
                        "foreach",
                        "save",
                        "body",
                    ]:
                        raise RMException("procedure can't be named %s" % procname)
                    procs[procname] = content
                else:
                    # no sense ?!
                    raise RMException("no action or too many : %s" % entry.keys())

            return ll

        list.__init__(self, feed(l))


###########################################################################
## Helpers
###########################################################################
def listFiles(path: str, filters=(".yml", ".rml")) -> T.Iterator[str]:
    for folder, subs, files in os.walk(path):
        if folder in [".", ".."] or (
            not os.path.basename(folder).startswith((".", "_"))
        ):
            for filename in files:
                if filename.lower().endswith(filters):
                    yield os.path.join(folder, filename)


def loadEnv(fd, varenvs: T.List[str] = []) -> dict:
    transform.path = None
    if fd:
        if not hasattr(fd, "name"):
            setattr(fd, "name", "")
        try:
            env = yamlLoad(fd) if fd else {}
            if fd.name:
                print(cw("Using '%s'" % os.path.relpath(fd.name)))
                transform.path = os.path.dirname(
                    fd.name
                )  # change path when executing transform methods, according the path of reqman.conf
        except Exception as e:
            raise RMException("YML syntax in %s\n%s" % (fd.name or "<string>", e))
    else:
        env = {}

    for name in varenvs:
        if name not in env:
            raise RMException("the switch '-%s' is unknown ?!" % name)
        else:
            dict_merge(env, env[name])
    return env


def render(reqs: T.List[Reqs], switchs: T.List[str]) -> T.Tuple[int, int, str]:
    h = """
<meta charset="utf-8">
<style>
body {font-family: sans-serif;font-size:90%}
.ok {color:green}
.ko {color:red}
hr {padding:0px;margin:0px;height: 1px;border: 0;color: #CCC;background-color: #CCC;}
pre {padding:4px;border:1px solid black;background:white !important;overflow-x:auto;width:100%;max-height:300px;margin:2px;}
span.title {cursor:pointer;}
span.title:hover {background:#EEE;}
i {float:right;color:#AAA}
i.bad {color:orange}
i.good {color:green}
ol,ul {margin:0px;}
ol {padding:0px;}
ol > li {background:#FFE;border-bottom:1px dotted grey;padding:4px;margin-left:16px}
li.hide {background:inherit}
li.hide > ul > span {display:none}
h3 {color:blue;margin:8 0 0 0;padding:0px}
.info {position:fixed;top:0px;right:0px;background:rgba(1,1,1,0.2);border-radius:4px;text-align:right;padding:4px}
.info > * {display:block}
p {margin:0px;padding:0px;color:#AAA;font-style: italic;}
</style>
"""
    alltr = []
    for f in reqs:
        times = [tr.res.time for tr in f.trs if tr.res and tr.res.time]

        hreqs = ""
        for tr in f.trs:
            alltr += tr

            qheaders = "\n".join(
                ["<b>%s</b>: %s" % (k, v) for k, v in list(tr.req.headers.items())]
            )
            content = Content(tr.req.body)
            qbody = html.escape(prettify(str(content or "")))

            qdoc = "<p>%s</p>" % tr.doc if tr.doc else ""

            if tr.res and tr.res.status is not None:
                rtime = tr.res.time
                info = tr.res.info
                rheaders = "\n".join(
                    ["<b>%s</b>: %s" % (k, v) for k, v in list(tr.res.headers.items())]
                )
                rbody = html.escape(prettify(str(tr.res.content or "")))

                hres = """
                    <pre title="the request">{tr.req.method} {tr.req.url}<hr/>{qheaders}<hr/>{qbody}</pre>
                    -> {info}
                    <pre title="the response">{rheaders}<hr/>{rbody}</pre>
                """.format(
                    **locals()
                )

            else:
                rtime = ""

                hres = """
                    <pre title="the request">{tr.req.method} {tr.req.url}<hr/>{qheaders}<hr/>{qbody}</pre>
                """.format(
                    **locals()
                )

            tests = "".join(
                [
                    """<li class='%s'>%s</li>"""
                    % ("ok" if t else "ko", html.escape(t.name))
                    for t in tr
                ]
            )

            hreqs += """
<li class="hide">
    <span class="title" onclick="this.parentElement.classList.toggle('hide')" title="Click to show/hide details"><b>{tr.req.method}</b> {tr.req.path} : <b>{tr.res}</b> <i>{rtime}</i>{qdoc}</span>
    <ul>
        <span>
            {hres}
        </span>
        {tests}
    </ul>
</li>
            """.format(
                **locals()
            )

        avg = sum(times, datetime.timedelta()) / len(times) if len(times) else 0
        h += """<h3>%s</h3>
        <ol>
            <i style='float:inherit'>%s req(s) avg = %s</i>
            %s
        </ol>""" % (
            f.name,
            len(times),
            avg,
            hreqs,
        )

    ok, total = len([i for i in alltr if i]), len(alltr)

    h += """<title>Result: %(ok)s/%(total)s</title>
    <div class='info'><span>%(today)s</span><b>%(switchs)s</b></div>""" % dict(
        ok=ok,
        total=total,
        today=str(datetime.datetime.now())[:16],
        switchs=" ".join(switchs),
    )

    return ok, total, h


def findRCUp(fromHere: str) -> T.Union[None, str]:
    """Find the rc in upwards folders"""
    current = os.path.realpath(fromHere)
    rc = None
    while 1:
        rc = os.path.join(current, REQMAN_CONF)
        if os.path.isfile(rc):
            break
        next = os.path.realpath(os.path.join(current, ".."))
        if next == current:
            rc = None
            break
        else:
            current = next
    return rc


def resolver(params: T.List) -> T.Tuple[T.Union[str, None], T.List[str]]:
    """ return tuple (reqman.conf,ymls) finded with params """
    ymls, paths = [], []

    # expand list with file pattern matching (win needed)
    params = list(itertools.chain.from_iterable([glob.glob(i) or [i] for i in params]))

    for p in params:
        if os.path.isdir(p):
            ymls += sorted(list(listFiles(p)), key=lambda x: x.lower())
            paths += [os.path.dirname(i) for i in ymls]
        elif os.path.isfile(p):
            paths.append(os.path.dirname(p))
            ymls.append(p)
        else:
            raise RMException("bad param: %s" % p)  # TODO: better here

    # choose first reqman.conf under choosen files
    rc = None
    folders = list(set(paths))
    folders.sort(key=lambda i: i.count("/") + i.count("\\"))
    for f in folders:
        if os.path.isfile(os.path.join(f, REQMAN_CONF)):
            rc = os.path.join(f, REQMAN_CONF)

    # if not, take the first reqman.conf in backwards
    if rc is None:
        rc = findRCUp(folders[0] if folders else ".")

    ymls.sort(key=lambda x: x.lower())
    return rc, ymls




def create(url: str) -> T.Tuple[T.Union[None, str], str]:
    """ return a (reqman.conf, yml_file) based on the test 'url' """
    hp = urllib.parse.urlparse(url)
    if hp and hp.scheme and hp.hostname:
        root = mkUrl(hp.scheme, hp.hostname, hp.port)
        rc = (
            """
root: %(root)s
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
"""
            % locals()
        )

    else:
        root = ""
        rc = None

    path = hp.path + ("?" + hp.query if hp.query else "")

    yml = (
        u"""# test created for "%(root)s%(path)s" !

- GET: %(path)s
#- GET: %(root)s%(path)s
  tests:
    - status: 200
"""
        % locals()
    )
    return (rc, yml)


class MainResponse:
    def __init__(self, rc, html=None, env={}, reqs=[], total=None, ok=None) -> None:
        self.code = rc
        self.html = html
        self.env = env
        self.reqs = reqs
        self.total = total
        self.ok = ok

class RC(int):
    """ a int with a details/mainResponse """
    def __new__(cls, value: int, details: MainResponse = None):
        s = super(RC, cls).__new__(cls, value)
        s.details = details
        return s



class OutputPrint(Enum):
    NO = 0
    YES = 1
    ONLYKO = 2


async def testContent(content: str, env: dict = {}) -> MainResponse:
    """ test a yml 'content' against env (easy wrapper for main call )"""
    reqs = [Reqs(io.StringIO(content), env)]
    return await main(reqs, env, paralleliz=False)


async def main(
    reqs, env: dict = {}, outputPrint: OutputPrint = OutputPrint.NO, switchsForHtml=[], paralleliz: bool = False
) -> MainResponse:
    

    atBegin=None
    atEnd=None
    
    if env and ("BEGIN" in env):
        r = io.StringIO("call: BEGIN")
        r.name = "BEGIN (%s)" % REQMAN_CONF
        atBegin = Reqs(r, env)

    if env and ("END" in env):
        r = io.StringIO("call: END")
        r.name = "END (%s)" % REQMAN_CONF
        atEnd = Reqs(r, env)
    
    async def proc(f,env):
        if outputPrint == OutputPrint.YES:
            print("\nTESTS:", cb(f.name))
        for t in f:
            tr = await t.test(env)  # TODO: colorful output !
            if outputPrint != OutputPrint.NO:
                if outputPrint == OutputPrint.ONLYKO:
                    if not all(tr):
                        print("\nTESTS:", cb(f.name))
                        print(tr)
                else:
                    print(tr)
            f.trs.append(tr)

    if atBegin: await proc(atBegin,env)
    if paralleliz:    
        ll=[]
        for i in reqs:
            senv=json.loads(json.dumps(env))
            ll.append( proc(i,senv) )
        await asyncio.gather(*ll)
    else:
        for i in reqs:
            senv=json.loads(json.dumps(env))
            await proc(i,senv)
    if atEnd: await proc(atEnd,env)

    if atBegin:reqs=[atBegin]+reqs
    if atEnd:reqs=reqs+[atEnd]

    ok, total, html = render(reqs, switchsForHtml)

    if outputPrint != OutputPrint.NO and total:
        print(
            "\nRESULT: ", (cg if int(ok) == int(total) else cr)("%s/%s" % (ok, total))
        )

    return MainResponse(int(total) - int(ok), html, env, reqs, total, ok)


async def commandLine(params: T.List[str] = []) -> RC:
    try:
        if len(params) == 2 and params[0].lower() == "new":
            ## CREATE USAGE
            rc = findRCUp(".")
            if rc:
                print(cw("Using '%s'" % os.path.relpath(rc)))

            conf, yml = create(params[1])
            if conf:
                if not rc:
                    print("Create", REQMAN_CONF)
                    with open(REQMAN_CONF, "w") as fid:
                        fid.write(conf)
            else:
                if not rc:
                    raise RMException(
                        "there is no '%s', you shoul provide a full url !" % REQMAN_CONF
                    )

            ff = glob.glob("*_test.rml")
            yname = "%04d_test.rml" % ((len(ff) + 1) * 10)

            print("Create", yname)
            with open(yname, "w") as fid:
                fid.write(yml)

            return RC(0)
        else:
            switchs = []

            # search for a specific env var (starting with "-")
            for switch in [i for i in params if i.startswith("-")]:
                params.remove(switch)
                switchs.append(switch[1:])

            if "-ko" in switchs:
                switchs.remove("-ko")
                onlyFailedTests = True
            else:
                onlyFailedTests = False

            if "-p" in switchs:
                switchs.remove("-p")
                paralleliz = True
                onlyFailedTests = True
            else:
                paralleliz = False

            rc, ymls = resolver(params)

            # load env !
            if rc:
                with open(str(rc), "r") as fid:
                    env = loadEnv(fid, switchs)
            else:
                env = loadEnv(None, switchs)

            ll = []
            for i in ymls:
                with open(i, "r") as fid:
                    ll.append(Reqs(fid, env))
            if ll:
                m = await main(
                    ll,
                    env,
                    OutputPrint.ONLYKO if onlyFailedTests else OutputPrint.YES,
                    switchs,
                    paralleliz
                )
                if m.code >= 0 and m.html:
                    with open("reqman.html", "w+", encoding="utf_8") as fid:
                        fid.write(m.html)
                return RC(m.code,m)  # aka rc
            else:
                print(
                    """USAGE TEST   : reqman [--option] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version %s
Test a http service with pre-made scenarios, whose are simple yaml files
(More info on https://github.com/manatlan/reqman)

<folder|file> : yml scenario or folder of yml scenario
                (as many as you want)

[option]
        --ko : limit standard output to failed tests (ko) only
        --p  : (BETA) paralleliz file tests (display only ko tests)
    """
                    % __version__
                )

                if env:
                    print(
                        """  [switch]      : default to "%s" """ % env.get("root", None)
                    )
                    for k, v in env.items():
                        root = v.get("root", None) if type(v) == dict else None
                        if root:
                            print("""%15s : "%s" """ % ("-" + k, root))
                else:
                    print(
                        """  [switch]      : pre-made 'switch' defined in a %s"""
                        % REQMAN_CONF
                    )
                return RC(-1)

    except RMException as e:
        print("\nERROR: %s" % e)
        return RC(-1)
    except Exception as e:
        print("\n**HERE IS A BUG**, please report it !")
        print(traceback.format_exc(), "\nERROR: %s" % e)
        return RC(-1)


def run() -> int:  # console_scripts for setup.py/commandLine
    loop = asyncio.get_event_loop()
    try:
        return int(loop.run_until_complete( commandLine(sys.argv[1:]) ) )
    except KeyboardInterrupt:
        print("\nERROR: process interrupted")
        # loop.run_until_complete(close())
        return -1

from io import StringIO

if __name__ == "__main__":
    sys.exit(run())

    # r=Request("https","www.manatlan.com",443,"GET","/")
    # x=asyncio.run( dohttp(r) )
    #~ from http.cookiejar import Cookie, CookieJar

    #~ cj = CookieJar()
    #~ try:
        #~ httpcore.Client().get(
            #~ "https://www.manatlan.com", timeout=httpcore.TimeoutConfig(5), cookies=cj
        #~ )
    #~ except httpcore.exceptions.ReadTimeout:
        #~ print(2)
