# -*- coding: utf-8 -*-
import wuy,sys,asyncio,os
import unittest


# Officiel unit tests (more than coverage 80% of code (cef works too), windows-mode only)

tests=[]

class UnitTests(wuy.Window):
    """
    <meta charset="utf-8" />
    <script>

    document.addEventListener("init", async function() {

        await wuy.report("declared var", wuy.val=="mémé" ,"")

        await testRequestPath("/unknown", r=>r.status==404 )
        await testRequestPath("/1", r=>r.status==200 && r.headers["content-type"].includes("text/html") )
        await testRequestPath("/2", r=>r.status==200 && r.headers["content-type"].includes("application/octet-stream") )
        await testRequestPath("/11", r=>r.status==201 && r.headers["content-type"].includes("text/html") )
        await testRequestPath("/12", r=>r.status==201 && r.headers["content-type"].includes("application/octet-stream") )
        await testRequestPath("/20", r=>r.status==202 && r.headers["content-type"].includes("text/plain") )
        await testRequestPath("/30", r=>r.status==203 && r.headers["content-type"].includes("text/plain") )

        await testBadCall("Test unknown proc",()=>wuy.unknown() );
        await testBadCall("Test call proc with bad number of params",()=>wuy.call(1) );
        await testBadCall("Test async call proc with bad number of params",()=>wuy.acall(1) );

        await wuy.report("Test good sync call", "abc" == await wuy.call('a','b','c') ,"")
        await wuy.report("Test good async call", "abc" == await wuy.acall('a','b','c') ,"")
        await wuy.report("Test good sync call", "abc" == await wuy.call('a','b') ,"")
        await wuy.report("Test good async call", "abc" == await wuy.acall('a','b') ,"")

        //---------------------------------------------------------
        // test a method which send a event

        r=await wuy.testEmit()
        wuy.on("pyEvent",async function(a,b,c) {
            await wuy.report("Test py/emit event recepted",a=="a" && b=="b" && c=="c","")
        })
        await wuy.report("Test py/emit return",r=="ok","")

        //---------------------------------------------------------
        // test wuy.emit() (not usefull in windows mode !)

        wuy.on("jsEvent",async function(a,b,c) { // not called in windows mode
            await wuy.report("jsEvent not received (normal)",False,"")  // it's bad !
        })
        var p=await wuy.emit("jsEvent",1,2,3)
        await wuy.report("Test js/emit return good things", p.length==3 && p[0]==1 && p[1]==2 && p[2]==3 ,"")

        //---------------------------------------------------------

        var content=await wuy.testWuyRequest()
        await wuy.report("Test wuy.request", content.includes("wuy.js") ,"")

        var content=await fetch("UnitTests.html").then( x=>x.text())
        await wuy.report("Test classic fetch", content.includes("wuy.js") ,"")

        //TODO: the givent port is arbitary ... change to self._port !
        var content=await wuy.fetch("http://localhost:8080/UnitTests.html").then( x=>x.text())  // need to have FULL URL !
        await wuy.report("Test wuy.fetch", content.includes("wuy.js") ,"")

        window.close()
    });

    async function testRequestPath(p,cbt) {
        var r=await fetch(p)
        var h={};
        for(var i of r.headers) h[ i[0] ] = i[1]
        var rep={status:r.status, headers:h, content: await r.text()}

        wuy.report(`Test path "${p}"`, cbt(rep), "Tests:"+cbt+" with:"+JSON.stringify(rep))
    }

    async function testBadCall(p,cbt) {
        try {
            await cbt()                 // raise an exception !
            wuy.report(p,false,"")
        }
        catch(e) {wuy.report(p,true,e)}
    }



    </script>

    """
    size=(100,100)

    async def report(self,libl,val,info):
        tests.append( (val,libl,info))

    #===========================================================================
    def request(self,req):    # async or not
        if req.path=="/1":
            return "text body"   # 200, text/html
        elif req.path=="/2":
            return b"text body"  # 200, application/octect-stream
        elif req.path=="/11":
            return wuy.Response(201,"text body")    # text/html
        elif req.path=="/12":
            return wuy.Response(201,b"text body")   # application/octect-stream
        elif req.path=="/20":
            return wuy.Response(202,"text body","text/plain")    # text/plain
        elif req.path=="/30":
            return wuy.Response(203,"text body",{"content-type":"text/plain"})

    def call(self,a,b,c="c"):
        return "%s%s%s" % (a,b,c)

    async def acall(self,a,b,c="c"):
        return "%s%s%s" % (a,b,c)

    def testEmit(self):
        self.emit("pyEvent","a","b","c")
        return "ok"

    async def testWuyRequest(self):
        #TODO: test POST too ! (only GET here)
        return (await wuy.request("http://localhost:%s/UnitTests.html" % self._port)).content

class TestWuy(unittest.TestCase):

    def test_isFreePort(self):
        ll=[wuy.isFree("localhost",p) for p in [22,23,445]]
        self.assertTrue( False in ll)

    def test_path(self):
        self.assertFalse(hasattr(sys,"_MEIPASS"))
        self.assertEqual(wuy.path("jo"),"jo")

    def test_pathFrozen(self):
        sys._MEIPASS="kiki"
        self.assertEqual(wuy.path("jo").replace("\\","/"),"kiki/jo")
        delattr(sys,"_MEIPASS")
        self.assertFalse(hasattr(sys,"_MEIPASS"))

    def test_getname(self):
        self.assertEqual( wuy.getname("jo"),"jo" )
        self.assertEqual( wuy.getname("jo.html"),"jo" )
        self.assertEqual( wuy.getname("jim/jo"),"jim.jo" )
        self.assertEqual( wuy.getname("jim/jo.html"),"jim.jo" )

    def test_aa_window_render_html(self):
        class aeff(wuy.Window):
            size=(100,100)
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)

        if os.path.isfile("web/aeff.html"): os.unlink("web/aeff.html")
        aeff()
        self.assertTrue( os.path.isfile("web/aeff.html") )
        os.unlink("web/aeff.html")

    def test_a_double_window(self):
        class aeff(wuy.Window):
            size=(100,100)
            "hello"
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)

        aeff()
        aeff()

    # def test_a_server(self):
    #     class saeff(wuy.Server):
    #         "I'm a server"
    #         def init(self):
    #             # asyncio.get_event_loop().call_later(2, self.exit)
    #             pass

    #     saeff()


    def test_a_window(self):
        global tests
        tests=[]
        UnitTests(log=True,val="mémé")

        print("#"*79)
        for test,libl,info in tests:
            print( test and "ok:" or "KO:",libl, "" if test is True else info)
        print("#"*79)

        self.assertEqual( len([ok for ok,*_ in tests if ok]),21)        # 21 tests ok


    # def test_a_windows(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__=="__main__":
    unittest.main()
